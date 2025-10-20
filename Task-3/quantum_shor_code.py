import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

# --- IMPORT NOISE MODEL FROM YOUR OTHER FILE ---
from quantum_noise_tester import noise_model

# --- Helper Function to Analyze Results (Unchanged) ---
def process_counts(counts):
    """
    Summarizes the counts dict into logical '0' and '1' outcomes.
    We are encoding logical |1>, so '0' is an error.
    """
    logical_0 = 0
    logical_1 = 0
    
    for (bitstring, count) in counts.items():
        logical_bit = bitstring.split(' ')[0] 
        
        if logical_bit == '0':
            logical_0 += count
        else:
            logical_1 += count
            
    total = logical_0 + logical_1
    if total == 0: return {'0': 0, '1': 0}, 0.0
    
    error_rate = logical_0 / total
    
    return {'0': logical_0, '1': logical_1}, error_rate

# --- Setup the Simulation ---
simulator = AerSimulator()
SHOTS = 4096
prob_x_error = 0.10
prob_z_error = 0.10

# --- Define GLOBAL Registers ---
NUM_DATA = 9
NUM_ANCILLA = 8 
qr = QuantumRegister(NUM_DATA + NUM_ANCILLA, 'q')
DATA_QUBITS = list(range(NUM_DATA))

cr_syn_x1 = ClassicalRegister(2, 'sx1')
cr_syn_x2 = ClassicalRegister(2, 'sx2')
cr_syn_x3 = ClassicalRegister(2, 'sx3')
cr_syn_z = ClassicalRegister(2, 'sz')
cr_log = ClassicalRegister(1, 'logical')

# --- Shor Code Components ---

def get_shor_encoder():
    """Returns the 9-qubit Shor code encoder circuit."""
    qc = QuantumCircuit(qr, cr_syn_x1, cr_syn_x2, cr_syn_x3, cr_syn_z, cr_log)
    
    qc.x(0)
    qc.barrier(label="Init |1>")

    # 1. Phase-flip encoding part (Outer code)
    qc.cx(0, 3)
    qc.cx(0, 6)
    qc.h([0, 3, 6])
    
    # 2. Bit-flip encoding part (Inner code)
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.cx(3, 4)
    qc.cx(3, 5)
    qc.cx(6, 7)
    qc.cx(6, 8)
    
    qc.barrier(label="Encode")
    return qc

def get_shor_syndrome_and_correction(qc):
    """Appends the full syndrome measurement and correction logic."""
    
    # === 1. Bit-Flip (X-Error) Detection ===
    qc.cx(0, 9)
    qc.cx(1, 9)
    qc.cx(1, 10)
    qc.cx(2, 10)
    qc.cx(3, 11)
    qc.cx(4, 11)
    qc.cx(4, 12)
    qc.cx(5, 12)
    qc.cx(6, 13)
    qc.cx(7, 13)
    qc.cx(7, 14)
    qc.cx(8, 14)
    
    qc.measure(9, cr_syn_x1[0])
    qc.measure(10, cr_syn_x1[1])
    qc.measure(11, cr_syn_x2[0])
    qc.measure(12, cr_syn_x2[1])
    qc.measure(13, cr_syn_x3[0])
    qc.measure(14, cr_syn_x3[1])
    
    qc.barrier(label="X-Syndrome")

    # === 2. Bit-Flip (X-Error) Correction ===
    with qc.if_test((cr_syn_x1, 1)): qc.x(0)
    with qc.if_test((cr_syn_x1, 2)): qc.x(2)
    with qc.if_test((cr_syn_x1, 3)): qc.x(1)
    with qc.if_test((cr_syn_x2, 1)): qc.x(3)
    with qc.if_test((cr_syn_x2, 2)): qc.x(5)
    with qc.if_test((cr_syn_x2, 3)): qc.x(4)
    with qc.if_test((cr_syn_x3, 1)): qc.x(6)
    with qc.if_test((cr_syn_x3, 2)): qc.x(8)
    with qc.if_test((cr_syn_x3, 3)): qc.x(7)

    qc.barrier(label="X-Correct")
    
    # === 3. Phase-Flip (Z-Error) Detection ===
    qc.h(DATA_QUBITS)
    for i in range(6): qc.cx(i, 15)
    for i in range(3, 9): qc.cx(i, 16)
    qc.h(DATA_QUBITS)
    
    qc.measure(15, cr_syn_z[0])
    qc.measure(16, cr_syn_z[1])
    
    qc.barrier(label="Z-Syndrome")
    
    # === 4. Phase-Flip (Z-Error) Correction ===
    with qc.if_test((cr_syn_z, 1)): qc.z([0, 1, 2])
    with qc.if_test((cr_syn_z, 2)): qc.z([6, 7, 8])
    with qc.if_test((cr_syn_z, 3)): qc.z([3, 4, 5])
        
    qc.barrier(label="Z-Correct")
    
    return qc

def get_shor_decoder_and_measure(qc):
    """Appends the (inverse) decoder and final measurement."""
    
    # 1. Bit-flip decoding (Inner code) - REVERSED ORDER
    qc.cx(6, 8) # Was cx(6, 7)
    qc.cx(6, 7) # Was cx(6, 8)
    
    qc.cx(3, 5) # Was cx(3, 4)
    qc.cx(3, 4) # Was cx(3, 5)

    qc.cx(0, 2) # Was cx(0, 1)
    qc.cx(0, 1) # Was cx(0, 2)
    
    # 2. Phase-flip decoding (Outer code) - This part was correct
    qc.h([0, 3, 6])
    qc.cx(0, 6)
    qc.cx(0, 3)

    qc.barrier(label="Decode")
    
    # Measure the logical qubit
    qc.measure(0, cr_log[0])
    return qc


# --- 1. IDEAL (NOISELESS) EXECUTION ---
print("--- 1. Ideal (Noiseless) Run ---")
qc_ideal = get_shor_encoder()
qc_ideal = get_shor_syndrome_and_correction(qc_ideal)
qc_ideal = get_shor_decoder_and_measure(qc_ideal)

job_ideal = simulator.run(qc_ideal, shots=SHOTS)
counts_ideal = job_ideal.result().get_counts(qc_ideal) 
logical_counts_ideal, error_ideal = process_counts(counts_ideal)

print(f"Full counts sample: {dict(list(counts_ideal.items())[:5])}...")
print(f"Logical state counts: {logical_counts_ideal}")
print(f"Logical Error Rate: {error_ideal * 100:.2f}%\n")


# --- 2. NOISY (NO QEC) EXECUTION ---
print("--- 2. Noisy Run (NO Correction) ---")
qc_no_qec = get_shor_encoder()
qc_noisy_no_qec = noise_model(prob_x_error, prob_z_error, qc_no_qec, target_qubits=DATA_QUBITS)
qc_noisy_no_qec = get_shor_decoder_and_measure(qc_noisy_no_qec)

job_no_qec = simulator.run(qc_noisy_no_qec, shots=SHOTS)
counts_no_qec = job_no_qec.result().get_counts(qc_noisy_no_qec)
logical_counts_no_qec, error_no_qec = process_counts(counts_no_qec)

print(f"Full counts sample: {dict(list(counts_no_qec.items())[:5])}...")
print(f"Logical state counts: {logical_counts_no_qec}")
print(f"Logical Error Rate: {error_no_qec * 100:.2f}%\n")


# --- 3. NOISY (WITH QEC) EXECUTION ---
print("--- 3. Noisy Run (WITH Correction) ---")
qc_qec_base = get_shor_encoder()
qc_noisy_qec = noise_model(prob_x_error, prob_z_error, qc_qec_base, target_qubits=DATA_QUBITS)
qc_noisy_qec = get_shor_syndrome_and_correction(qc_noisy_qec)
qc_noisy_qec = get_shor_decoder_and_measure(qc_noisy_qec)

job_qec = simulator.run(qc_noisy_qec, shots=SHOTS)
counts_qec = job_qec.result().get_counts(qc_noisy_qec) 
logical_counts_qec, error_qec = process_counts(counts_qec)

print(f"Full counts sample: {dict(list(counts_qec.items())[:5])}...")
print(f"Logical state counts: {logical_counts_qec}")
print(f"Logical Error Rate: {error_qec * 100:.2f}%\n")