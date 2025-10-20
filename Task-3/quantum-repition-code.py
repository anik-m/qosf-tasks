import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit_aer.noise import QuantumError, pauli_error 

# --- TASK 1: NOISE MODEL FUNCTION (Corrected) ---
def noise_model(a, b, circuit, target_qubits):
    """
    Given a circuit, it adds a pauli X with "a" probability 
    and pauli Z with "b" probability to the specified target_qubits.
    """
    if a + b > 1.0:
        raise ValueError("Sum of probabilities 'a' and 'b' cannot exceed 1.0")
        
    prob_identity = 1.0 - a - b
    error_channel = pauli_error([('X', a), ('Z', b), ('I', prob_identity)])
    
    circuit_with_noise = circuit.copy()
    
    for i in target_qubits:
        circuit_with_noise.append(error_channel, [i])
    
    return circuit_with_noise

# --- Helper Function to Analyze Results ---
def process_counts(counts):
    """
    Summarizes the counts dict into logical '0' and '1' outcomes.
    The Qiskit bitstring is 'logical_bit syndrome_bits'.
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
    
    # We intended to encode '1', so any '0' is an error.
    error_rate = logical_0 / total
    
    return {'0': logical_0, '1': logical_1}, error_rate

# --- Setup the Simulation ---
simulator = AerSimulator()
SHOTS = 4096

# As requested: Only X errors
prob_x_error = 0.20  # 20% chance of an X error
prob_z_error = 0.0

DATA_QUBITS = [0, 1, 2]

# --- Define GLOBAL Registers ---
# These will be used by all circuit-building functions
q_data = 3
q_ancilla = 2
qr = QuantumRegister(q_data + q_ancilla, 'q')
cr_syn = ClassicalRegister(2, 'syndrome')
cr_log = ClassicalRegister(1, 'logical')

def get_encoder():
    """Returns the initialization and encoding circuit."""
    # Use the GLOBAL registers defined above
    qc = QuantumCircuit(qr, cr_syn, cr_log)
    
    # Initialize logical qubit q[0] to |1>
    qc.x(0) 
    qc.barrier(label="Init |1>")
    # Encode: |100> -> |111>
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.barrier(label="Encode")
    return qc

def get_syndrome_and_correction(qc):
    """Appends the syndrome and correction logic to a circuit."""
    # Syndrome measurement
    qc.cx(0, 3) # Parity (q0, q1) -> q3 (syndrome[0])
    qc.cx(1, 3)
    
    qc.cx(1, 4) # Parity (q1, q2) -> q4 (syndrome[1])
    qc.cx(2, 4)
    qc.barrier(label="Syndrome")
    
    # Measure syndromes into GLOBAL register
    qc.measure(3, cr_syn[0]) # q[3] -> syndrome[0]
    qc.measure(4, cr_syn[1]) # q[4] -> syndrome[1]
    qc.barrier(label="Correction")

    # --- THIS IS THE FIX ---
    # Apply correction based on classical syndrome bits
    
    # cr_syn == 1 (binary '01'): s[0]=1, s[1]=0 -> Error on q[0]
    with qc.if_test((cr_syn, 1)):
        qc.x(0) # Was qc.x(2)
        
    # cr_syn == 2 (binary '10'): s[0]=0, s[1]=1 -> Error on q[2]
    with qc.if_test((cr_syn, 2)):
        qc.x(2) # Was qc.x(0)
        
    # cr_syn == 3 (binary '11'): s[0]=1, s[1]=1 -> Error on q[1]
    with qc.if_test((cr_syn, 3)):
        qc.x(1) # This was correct
        
    return qc

def get_decoder_and_measure(qc):
    """Appends the un-encoding and final measurement."""
    qc.barrier(label="Decode")
    # Un-encode: |111> -> |100>
    qc.cx(0, 2)
    qc.cx(0, 1)
    qc.barrier()
    # Measure the logical qubit into GLOBAL register
    qc.measure(0, cr_log[0]) # q[0] -> logical[0]
    return qc


# --- 1. IDEAL (NOISELESS) EXECUTION ---
print("--- 1. Ideal (Noiseless) Run ---")
qc_ideal = get_encoder()
qc_ideal = get_syndrome_and_correction(qc_ideal)
qc_ideal = get_decoder_and_measure(qc_ideal)

job_ideal = simulator.run(qc_ideal, shots=SHOTS)
counts_ideal = job_ideal.result().get_counts(qc_ideal) 
logical_counts_ideal, error_ideal = process_counts(counts_ideal)

print(f"Full counts (logical syndrome): {counts_ideal}")
print(f"Logical state counts: {logical_counts_ideal}")
print(f"Logical Error Rate: {error_ideal * 100:.2f}%\n")


# --- 2. NOISY (NO QEC) EXECUTION ---
print("--- 2. Noisy Run (NO Correction) ---")
qc_no_qec = get_encoder()
qc_noisy_no_qec = noise_model(prob_x_error, prob_z_error, qc_no_qec, target_qubits=DATA_QUBITS)
qc_noisy_no_qec = get_decoder_and_measure(qc_noisy_no_qec)

job_no_qec = simulator.run(qc_noisy_no_qec, shots=SHOTS)
counts_no_qec = job_no_qec.result().get_counts(qc_noisy_no_qec)
logical_counts_no_qec, error_no_qec = process_counts(counts_no_qec)

print(f"Full counts (logical syndrome): {counts_no_qec}")
print(f"Logical state counts: {logical_counts_no_qec}")
print(f"Logical Error Rate: {error_no_qec * 100:.2f}%\n")


# --- 3. NOISY (WITH QEC) EXECUTION ---
print("--- 3. Noisy Run (WITH Correction) ---")
qc_qec_base = get_encoder()
qc_noisy_qec = noise_model(prob_x_error, prob_z_error, qc_qec_base, target_qubits=DATA_QUBITS)
qc_noisy_qec = get_syndrome_and_correction(qc_noisy_qec)
qc_noisy_qec = get_decoder_and_measure(qc_noisy_qec)

job_qec = simulator.run(qc_noisy_qec, shots=SHOTS)
counts_qec = job_qec.result().get_counts(qc_noisy_qec) 
logical_counts_qec, error_qec = process_counts(counts_qec)

print(f"Full counts (logical syndrome): {counts_qec}")
print(f"Logical state counts: {logical_counts_qec}")
print(f"Logical Error Rate: {error_qec * 100:.2f}%\n")

# print("\n--- Full QEC Circuit Diagram (for inspection) ---")
# print(qc_noisy_qec.draw())