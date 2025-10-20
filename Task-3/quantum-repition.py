import qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit_aer.noise import QuantumError, pauli_error 

# --- TASK 1: NOISE MODEL FUNCTION (Corrected) ---
# We will use this function to inject noise.

def noise_model(a, b, circuit):
    """
    Given a circuit, it adds a pauli X with "a" probability 
    and pauli Z with "b" probability to each qubit.
    """
    if a + b > 1.0:
        raise ValueError("Sum of probabilities 'a' and 'b' cannot exceed 1.0")
        
    prob_identity = 1.0 - a - b
    error_channel = pauli_error([('X', a), ('Z', b), ('I', prob_identity)])
    
    circuit_with_noise = circuit.copy()
    num_qubits = circuit.num_qubits
    
    # Apply the 1-qubit error to each qubit individually
    for i in range(num_qubits):
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
        # The logical bit is the first one in the string
        logical_bit = bitstring.split(' ')[0] 
        
        if logical_bit == '0':
            logical_0 += count
        else:
            logical_1 += count
            
    total = logical_0 + logical_1
    if total == 0: return {'0': 0, '1': 0}, 0.0
    
    # Calculate the Logical Error Rate
    # We intended to encode '1', so any '0' is an error.
    error_rate = logical_0 / total
    
    return {'0': logical_0, '1': logical_1}, error_rate

# --- Setup the Simulation ---

simulator = AerSimulator()
SHOTS = 4096

# As requested: Only X errors
prob_x_error = 0.20  # 20% chance of an X error
prob_z_error = 0.0

# --- Define Circuit Components ---

# We need 3 data qubits and 2 syndrome (ancilla) qubits
q_data = 3
q_ancilla = 2
qr = QuantumRegister(q_data + q_ancilla, 'q')

# We need 2 classical bits for syndrome and 1 for the final logical state
cr_syn = ClassicalRegister(2, 'syndrome')
cr_log = ClassicalRegister(1, 'logical')

# We will test by encoding the logical state |1>
def get_encoder():
    """Returns the initialization and encoding circuit."""
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
    # Syndrome measurement: Check parity
    # q[0] vs q[1] -> syndrome[0] (q[3])
    qc.cx(0, 3)
    qc.cx(1, 3)
    # q[1] vs q[2] -> syndrome[1] (q[4])
    qc.cx(1, 4)
    qc.cx(2, 4)
    qc.barrier(label="Syndrome")
    
    # Measure syndromes
    qc.measure(3, 0) # q[3] -> syndrome[0]
    qc.measure(4, 1) # q[4] -> syndrome[1]
    qc.barrier(label="Correction")

    # Apply correction based on classical syndrome bits
    # c_if(classical_register, integer_value)
    # '01' (binary) = 1 (int) -> Error on q[2]
    qc.x(2).c_if(cr_syn, 1) 
    # '10' (binary) = 2 (int) -> Error on q[0]
    qc.x(0).c_if(cr_syn, 2)
    # '11' (binary) = 3 (int) -> Error on q[1]
    qc.x(1).c_if(cr_syn, 3)
    return qc

def get_decoder_and_measure(qc):
    """Appends the un-encoding and final measurement."""
    qc.barrier(label="Decode")
    # Un-encode: |111> -> |100>
    qc.cx(0, 2)
    qc.cx(0, 1)
    qc.barrier()
    # Measure the logical qubit
    qc.measure(0, 2) # q[0] -> logical[0]
    return qc


# --- 1. IDEAL (NOISELESS) EXECUTION ---
print("--- 1. Ideal (Noiseless) Run ---")
qc_ideal = get_encoder()
qc_ideal = get_syndrome_and_correction(qc_ideal)
qc_ideal = get_decoder_and_measure(qc_ideal)

job_ideal = simulator.run(qc_ideal, shots=SHOTS)
counts_ideal = job_ideal.result().get_counts()
logical_counts_ideal, error_ideal = process_counts(counts_ideal)

print(f"Full counts (logical syndrome): {counts_ideal}")
print(f"Logical state counts: {logical_counts_ideal}")
print(f"Logical Error Rate: {error_ideal * 100:.2f}%\n")


# --- 2. NOISY (NO QEC) EXECUTION ---
print("--- 2. Noisy Run (NO Correction) ---")
# Build circuit: Encode -> Noise -> Decode
qc_no_qec = get_encoder()

# Apply noise right after encoding
qc_noisy_no_qec = noise_model(prob_x_error, prob_z_error, qc_no_qec)

# Skip syndrome/correction, just decode and measure
qc_noisy_no_qec = get_decoder_and_measure(qc_noisy_no_qec)

job_no_qec = simulator.run(qc_noisy_no_qec, shots=SHOTS)
counts_no_qec = job_no_qec.result().get_counts()
logical_counts_no_qec, error_no_qec = process_counts(counts_no_qec)

print(f"Full counts (logical syndrome): {counts_no_qec}")
print(f"Logical state counts: {logical_counts_no_qec}")
print(f"Logical Error Rate: {error_no_qec * 100:.2f}%\n")


# --- 3. NOISY (WITH QEC) EXECUTION ---
print("--- 3. Noisy Run (WITH Correction) ---")
# Build circuit: Encode -> Noise -> Syndrome -> Correct -> Decode
qc_qec_base = get_encoder()

# Apply noise right after encoding
qc_noisy_qec = noise_model(prob_x_error, prob_z_error, qc_qec_base)

# NOW, add the QEC parts
qc_noisy_qec = get_syndrome_and_correction(qc_noisy_qec)
qc_noisy_qec = get_decoder_and_measure(qc_noisy_qec)

job_qec = simulator.run(qc_noisy_qec, shots=SHOTS)
counts_qec = job_qec.result().get_counts()
logical_counts_qec, error_qec = process_counts(counts_qec)

print(f"Full counts (logical syndrome): {counts_qec}")
print(f"Logical state counts: {logical_counts_qec}")
print(f"Logical Error Rate: {error_qec * 100:.2f}%\n")

print("\n--- Full QEC Circuit Diagram ---")
print(qc_noisy_qec)
