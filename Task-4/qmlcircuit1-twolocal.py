import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import warnings

# --- CHANGES START HERE ---
# REMOVED: from qiskit import BasicAer
# REMOVED: from qiskit.utils import QuantumInstance, algorithm_globals
# ADDED:
from qiskit_aer.primitives import Sampler as AerSampler # Use the fast simulator
# --- CHANGES END HERE ---

from qiskit.circuit.library import ZZFeatureMap, PauliFeatureMap, TwoLocal
from qiskit_machine_learning.algorithms.classifiers import VQC

# Suppress warnings
warnings.filterwarnings('ignore')

# Set random seed
seed = 42

# --- 1. Load and prepare the new dataset ---
iris = load_iris()
X_full = iris.data
y_full = iris.target

X_filtered = X_full[(y_full == 1) | (y_full == 2)]
y_filtered = y_full[(y_full == 1) | (y_full == 2)]
y_filtered = y_filtered - 1 

print(f"Original data shape (Versicolor vs Virginica): {X_filtered.shape}")
print(f"Labels: {np.unique(y_filtered)}")
print("---" * 20)

# --- 2. Proposal A: 2-Qubit Model with PCA ---
print("Running Proposal A (2-Qubit, PCA)...")

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_filtered)
scaler_A = MinMaxScaler(feature_range=(0, np.pi))
X_scaled_A = scaler_A.fit_transform(X_pca)

X_train_A, X_test_A, y_train_A, y_test_A = train_test_split(
    X_scaled_A, y_filtered, test_size=0.3, random_state=seed
)

feature_map_A = ZZFeatureMap(feature_dimension=2, reps=2)
ansatz_A = TwoLocal(num_qubits=2, rotation_blocks='ry', 
                    entanglement_blocks='cz', entanglement='linear', reps=3)

# --- CHANGES START HERE ---
# Define the sampler
# We use AerSampler for performance and to set the seed
sampler = AerSampler(run_options={'seed': seed})

# REMOVED: qi_A = QuantumInstance(...)
vqc_A = VQC(feature_map=feature_map_A,
            ansatz=ansatz_A,
            sampler=sampler) # Pass the sampler
# --- CHANGES END HERE ---

print("Training Proposal A...")
vqc_A.fit(X_train_A, y_train_A)
score_A = vqc_A.score(X_test_A, y_test_A)

print(f"Accuracy Proposal A (2-Qubit, PCA): {score_A:.4f}")
print("---" * 20)


# --- 3. Proposal B: 4-Qubit Model with All Features ---
print("Running Proposal B (4-Qubit, All Features)...")

scaler_B = MinMaxScaler(feature_range=(0, np.pi))
X_scaled_B = scaler_B.fit_transform(X_filtered)

X_train_B, X_test_B, y_train_B, y_test_B = train_test_split(
    X_scaled_B, y_filtered, test_size=0.3, random_state=seed
)

feature_map_B = PauliFeatureMap(feature_dimension=4, reps=1, paulis=['Z'])
ansatz_B = TwoLocal(num_qubits=4, rotation_blocks=['ry', 'rz'], 
                    entanglement_blocks='cx', entanglement='circular', reps=2)

# --- CHANGES START HERE ---
# We can re-use the same sampler instance
# REMOVED: qi_B = QuantumInstance(...)
vqc_B = VQC(feature_map=feature_map_B,
            ansatz=ansatz_B,
            sampler=sampler) # Pass the sampler
# --- CHANGES END HERE ---

print("Training Proposal B...")
vqc_B.fit(X_train_B, y_train_B)
score_B = vqc_B.score(X_test_B, y_test_B)

print(f"Accuracy Proposal B (4-Qubit, All Features): {score_B:.4f}")
print("---" * 20)

# --- 4. Final Comparison ---
print("\nFinal Results (Versicolor vs Virginica):")
print(f"Proposal A (2-Qubit, PCA): {score_A:.4f}")
print(f"Proposal B (4-Qubit, All Features): {score_B:.4f}")
