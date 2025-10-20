import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

# --- IMPORT NOISE MODEL FROM YOUR OTHER FILE ---
from quantum_noise_tester import noise_model

# --- Helper Function to Analyze Results ---
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

# --- Define GLOBAL Registers (for construction) ---
NUM_DATA = 7
NUM_ANCILLA = 6
qr = QuantumRegister(NUM_DATA + NUM_ANCILLA, 'q')
DATA_QUBITS = list(range(NUM_DATA))

cr_syn_z = ClassicalRegister(3, 'sz') # For X-error correction
cr_syn_x = ClassicalRegister(3, 'sx') # For Z-error correction
cr_log = ClassicalRegister(1, 'logical')

# --- Steane Code Components ---

def get_steane_encoder():
    """Encodes q[0] into a 7-qubit logical state [q0-q6]."""
    qc = QuantumCircuit(qr, cr_syn_z, cr_syn_x, cr_log)
    
    # Encoder for logical |0>
    qc.h([0, 1, 2])
    qc.cx(0, 4)
    qc.cx(0, 5)
    qc.cx(0, 6)
    qc.cx(1, 3)
    qc.cx(1, 5)
    qc.cx(1, 6)
    qc.cx(2, 3)
    qc.cx(2, 4)
    qc.cx(2, 6)
    
    qc.barrier(label="Encode |0>")
    qc.x([0, 1, 2]) # Apply Logical-X to get |1>_L
    qc.barrier(label="Encode |1>")
    
    return qc

def get_steane_syndrome_and_correction(qc):
    """Appends syndrome measurement and correction logic."""
    
    # Get registers from the circuit object
    local_cr_syn_z = qc.cregs[0] 
    local_cr_syn_x = qc.cregs[1]
    
    # === 1. Z-Syndromes (for X-error detection) ===
    # g1 = Z0 Z4 Z5 Z6
    qc.cx(0, 7); qc.cx(4, 7); qc.cx(5, 7); qc.cx(6, 7)
    # g2 = Z1 Z3 Z5 Z6
    qc.cx(1, 8); qc.cx(3, 8); qc.cx(5, 8); qc.cx(6, 8)
    # g3 = Z2 Z3 Z4 Z6
    qc.cx(2, 9); qc.cx(3, 9); qc.cx(4, 9); qc.cx(6, 9)

    qc.measure(7, local_cr_syn_z[0])
    qc.measure(8, local_cr_syn_z[1])
    qc.measure(9, local_cr_syn_z[2])
    qc.barrier(label="Z-Syndrome")

    # === 2. X-Syndromes (for Z-error detection) ===
    qc.h(DATA_QUBITS)
    # g4 = X0 X4 X5 X6
    qc.cx(0, 10); qc.cx(4, 10); qc.cx(5, 10); qc.cx(6, 10)
    # g5 = X1 X3 X5 X6
    qc.cx(1, 11); qc.cx(3, 11); qc.cx(5, 11); qc.cx(6, 11)
    # g6 = X2 X3 X4 X6
    qc.cx(2, 12); qc.cx(3, 12); qc.cx(4, 12); qc.cx(6, 12)
    qc.h(DATA_QUBITS)

    qc.measure(10, local_cr_syn_x[0])
    qc.measure(11, local_cr_syn_x[1])
    qc.measure(12, local_cr_syn_x[2])
    qc.barrier(label="X-Syndrome")

    # === 3. Correction Logic (FIXED MAPPING) ===
    # Syndrome is measured as 'g3 g2 g1' or 'g6 g5 g4' (Qiskit bit order)
    
    # X-Error Correction (based on Z-syndrome 'sz')
    # sz = 's3 s2 s1'
    with qc.if_test((local_cr_syn_z, 1)): qc.x(0) # 001 -> X(0)
    with qc.if_test((local_cr_syn_z, 2)): qc.x(1) # 010 -> X(1)
    with qc.if_test((local_cr_syn_z, 3)): qc.x(5) # 011 -> X(5)
    with qc.if_test((local_cr_syn_z, 4)): qc.x(2) # 100 -> X(2)
    with qc.if_test((local_cr_syn_z, 5)): qc.x(4) # 101 -> X(4)
    with qc.if_test((local_cr_syn_z, 6)): qc.x(3) # 110 -> X(3)
    with qc.if_test((local_cr_syn_z, 7)): qc.x(6) # 111 -> X(6)

    # Z-Error Correction (based on X-syndrome 'sx')
    # sx = 's6 s5 s4'
    with qc.if_test((local_cr_syn_x, 1)): qc.z(0) # 001 -> Z(0)
    with qc.if_test((local_cr_syn_x, 2)): qc.z(1) # 010 -> Z(1)
    with qc.if_test((local_cr_syn_x, 3)): qc.z(5) # 011 -> Z(5)
    with qc.if_test((local_cr_syn_x, 4)): qc.z(2) # 100 -> Z(2)
    with qc.if_test((local_cr_syn_x, 5)): qc.z(4) # 101 -> Z(4)
    with qc.if_test((local_cr_syn_x, 6)): qc.z(3) # 110 -> Z(3)
    with qc.if_test((local_cr_syn_x, 7)): qc.z(6) # 111 -> Z(6)
    
    qc.barrier(label="Correction")
    return qc

def get_steane_decoder_and_measure(qc):
    """Appends the (inverse) decoder and final measurement."""
    
    local_cr_log = qc.cregs[2]
    
    # Undo the Logical-X to get back to |0>
    qc.x([0, 1, 2]) 
    
    # Decoder (inverse of encoder)
    qc.cx(2, 6)
    qc.cx(2, 4)
    qc.cx(2, 3)
    qc.cx(1, 6)
    qc.cx(1, 5)
    qc.cx(1, 3)
    qc.cx(0, 6)
    qc.cx(0, 5)
    qc.cx(0, 4)
    qc.h([0, 1, 2])
    
    qc.barrier(label="Decode")
    
    # Flip back to |1> for our helper function
    qc.x(0)
    qc.measure(0, local_cr_log[0])
    return qc


# --- 1. IDEAL (NOISELESS) EXECUTION ---
print("--- 1. Ideal (Noiseless) Run ---")
qc_ideal = get_steane_encoder()
qc_ideal = get_steane_syndrome_and_correction(qc_ideal)
qc_ideal = get_steane_decoder_and_measure(qc_ideal)

job_ideal = simulator.run(qc_ideal, shots=SHOTS)
counts_ideal = job_ideal.result().get_counts(qc_ideal) 
logical_counts_ideal, error_ideal = process_counts(counts_ideal)

print(f"Full counts sample: {dict(list(counts_ideal.items())[:5])}...")
print(f"Logical state counts: {logical_counts_ideal}")
print(f"Logical Error Rate: {error_ideal * 100:.2f}%\n")


# --- 2. NOISY (NO QEC) EXECUTION ---
print("--- 2. Noisy Run (NO Correction) ---")
qc_no_qec = get_steane_encoder()
qc_noisy_no_qec = noise_model(prob_x_error, prob_z_error, qc_no_qec, target_qubits=DATA_QUBITS)
qc_noisy_no_qec = get_steane_decoder_and_measure(qc_noisy_no_qec)

job_no_qec = simulator.run(qc_noisy_no_qec, shots=SHOTS)
counts_no_qec = job_no_qec.result().get_counts(qc_noisy_no_qec)
logical_counts_no_qec, error_no_qec = process_counts(counts_no_qec)

print(f"Full counts sample: {dict(list(counts_no_qec.items())[:5])}...")
print(f"Logical state counts: {logical_counts_no_qec}")
print(f"Logical Error Rate: {error_no_qec * 100:.2f}%\n")


# --- 3. NOISY (WITH QEC) EXECUTION ---
print("--- 3. Noisy Run (WITH Correction) ---")
qc_qec_base = get_steane_encoder()
qc_noisy_qec = noise_model(prob_x_error, prob_z_error, qc_qec_base, target_qubits=DATA_QUBITS)
qc_noisy_qec = get_steane_syndrome_and_correction(qc_noisy_qec)
qc_noisy_qec = get_steane_decoder_and_measure(qc_noisy_qec)

job_qec = simulator.run(qc_noisy_qec, shots=SHOTS)
counts_qec = job_qec.result().get_counts(qc_noisy_qec) 
logical_counts_qec, error_qec = process_counts(counts_qec)

print(f"Full counts sample: {dict(list(counts_qec.items())[:5])}...")
print(f"Logical state counts: {logical_counts_qec}")
print(f"Logical Error Rate: {error_qec * 100:.2f}%\n")