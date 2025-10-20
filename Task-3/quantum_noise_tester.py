import qiskit
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
# Corrected import for Qiskit 1.x
from qiskit_aer.noise import QuantumError, pauli_error 

def noise_model(a, b, circuit, target_qubits):
    """
    Given a circuit, it adds a pauli X with "a" probability 
    and pauli Z with "b" probability to the specified target_qubits.
    
    Args:
        a (float): Probability of a Pauli X error.
        b (float): Probability of a Pauli Z error
        circuit (QuantumCircuit): The ideal input circuit.
        target_qubits (list[int]): A list of qubit indices to apply noise to.
        
    Returns:
        QuantumCircuit: A new circuit object with the noise channel appended.
    """
    
    # Check that probabilities are valid
    if a + b > 1.0:
        raise ValueError("Sum of probabilities 'a' and 'b' cannot exceed 1.0")
        
    # Calculate the probability of no error (Identity)
    prob_identity = 1.0 - a - b
    
    # Create the 1-qubit Pauli error channel
    error_channel = pauli_error([('X', a), ('Z', b), ('I', prob_identity)])
    
    # Create a new circuit by copying the ideal one
    circuit_with_noise = circuit.copy()
    
    # Apply the 1-qubit error only to the target qubits
    for i in target_qubits:
        circuit_with_noise.append(error_channel, [i])
    
    return circuit_with_noise

# --- Test Script ---

# Get the Aer simulator
simulator = AerSimulator()

# ---------------------------------
# ## 1. 1-Qubit Test (Prepare |1>)
# ---------------------------------
print("## 1. 1-Qubit Test (Prepare |1>)")
qc_base = QuantumCircuit(1)
qc_base.x(0)  # Flip the |0> state to |1>

# --- 1a. Ideal ---
qc_ideal = qc_base.copy()
qc_ideal.measure_all()
job_ideal = simulator.run(qc_ideal, shots=1024)
counts_ideal = job_ideal.result().get_counts()
print(f"Ideal counts: {counts_ideal}")

# --- 1b. Noisy ---
prob_x_error = 0.25
prob_z_error = 0.25
# Use the updated function, specifying the target qubit
qc_noisy = noise_model(prob_x_error, prob_z_error, qc_base, target_qubits=[0])
qc_noisy.measure_all()
job_noisy = simulator.run(qc_noisy, shots=1024)
counts_noisy = job_noisy.result().get_counts()
print(f"Noisy counts: {counts_noisy}")
print("---")


# ---------------------------------
# ## 2. 2-Qubit Entanglement (Bell State)
# ---------------------------------
print("## 2. 2-Qubit Entanglement (Bell State)")

qc_bell_base = QuantumCircuit(2)
qc_bell_base.h(0)
qc_bell_base.cx(0, 1)

# --- 2a. Ideal Bell State ---
qc_bell_ideal = qc_bell_base.copy()
qc_bell_ideal.measure_all()
job_bell_ideal = simulator.run(qc_bell_ideal, shots=1024)
counts_bell_ideal = job_bell_ideal.result().get_counts()
print(f"Ideal Bell counts: {counts_bell_ideal}")

# --- 2b. Noisy Bell State ---
# Use the updated function, specifying target qubits
qc_bell_noisy = noise_model(prob_x_error, prob_z_error, qc_bell_base, target_qubits=[0, 1])
qc_bell_noisy.measure_all()
job_bell_noisy = simulator.run(qc_bell_noisy, shots=1024)
counts_bell_noisy = job_bell_noisy.result().get_counts()
print(f"Noisy Bell counts: {counts_bell_noisy}")
print("---")