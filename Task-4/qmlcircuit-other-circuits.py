import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import warnings
import time

# Qiskit Imports
from qiskit_aer.primitives import Sampler as AerSampler
from qiskit.circuit.library import (
    PauliFeatureMap, 
    TwoLocal, 
    EfficientSU2, 
    RealAmplitudes
)
from qiskit_machine_learning.algorithms.classifiers import VQC

# ---  Setup ---
warnings.filterwarnings('ignore')
seed = 42

# ---  Data Preparation (Versicolor vs Virginica) ---
print("Preparing data (Versicolor vs Virginica, 4 features)...")
iris = load_iris()
X_full = iris.data
y_full = iris.target

# Filter for Versicolor (1) and Virginica (2)
X_filtered = X_full[(y_full == 1) | (y_full == 2)]
y_filtered = y_full[(y_full == 1) | (y_full == 2)]

# Remap labels {1, 2} -> {0, 1}
y_filtered = y_filtered - 1 

# Scale all 4 features to [0, pi]
scaler = MinMaxScaler(feature_range=(0, np.pi))
X_scaled = scaler.fit_transform(X_filtered)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_filtered, test_size=0.3, random_state=seed
)
print(f"Training on {len(y_train)} samples, testing on {len(y_test)} samples.")

# ---  Define Common Quantum Components ---
# Sampler (for all models)
# We use the fast Aer simulator and set a seed for reproducibility
sampler = AerSampler(run_options={'seed': seed})

# Feature Map (for all models)
# Using the 4-qubit PauliFeatureMap from our "Proposal B"
feature_map = PauliFeatureMap(feature_dimension=4, reps=1, paulis=['Z'])

# ---  Define and Run All Models ---

# We'll use reps=2 for all ansatze to keep the comparison as fair as possible
reps = 2

# Define all the ansatze we want to test
ansatze = {
    "1. TwoLocal (Circular)": TwoLocal(num_qubits=4, rotation_blocks=['ry', 'rz'], 
                                       entanglement_blocks='cx', entanglement='circular', 
                                       reps=reps),
    
    "2. EfficientSU2 (Circular)": EfficientSU2(num_qubits=4, entanglement='circular', 
                                              reps=reps),
    
    "3. TwoLocal (SCA)": TwoLocal(num_qubits=4, rotation_blocks=['ry', 'rz'], 
                                  entanglement_blocks='cx', entanglement='sca', 
                                  reps=reps),
    
    "4. TwoLocal (RZZ Entangler)": TwoLocal(num_qubits=4, rotation_blocks=['ry', 'rz'], 
                                           entanglement_blocks='rzz', entanglement='circular', 
                                           reps=reps),
    
    "5. RealAmplitudes (Circular)": RealAmplitudes(num_qubits=4, entanglement='circular', 
                                                   reps=reps)
}

# Dictionary to store the results
results = {}

print("\n---" * 20)
print("Starting Model Bake-Off...")

# Loop, train, and score each model
for name, ansatz in ansatze.items():
    print(f"\nTraining Model {name}...")
    start_time = time.time()
    
    vqc = VQC(feature_map=feature_map,
              ansatz=ansatz,
              sampler=sampler)
    
    vqc.fit(X_train, y_train)
    score = vqc.score(X_test, y_test)
    
    end_time = time.time()
    
    results[name] = score
    print(f"Score: {score:.4f} (Training time: {end_time - start_time:.2f}s)")

# ---  Final Comparison ---
print("\n---" * 20)
print("Final Model Comparison (Versicolor vs Virginica):")
print("---" * 20)
for name, score in results.items():
    print(f"- {name}: {score:.4f}")
