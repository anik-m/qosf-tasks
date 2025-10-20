# qosf-tasks
This repo contains the tasks in the appropriately named folders.

---
## Task-1
Here the proof for the the choices of the parameters is shown along with its verification via code.

---
## Task-2
Here the implementation for the quantum state preparing function is there with all required constraints (Ensuring normalization, catching zero vectors).

It can be used interactively for n qubits, provided 2<sup>n</sup> amplitude values are provided.

Tests are also written that can be easily checked using pytest, while also adding more possible tests easily.

---
## Task-3

Here the implementations of the noise model and the various codes are placed and run together in the notebook for comparison and general ideas from trying repitition, shor, and hamming codes. 

---
## Task-4

### ⚛️ Quantum Machine Learning for Iris Classification

This task designs and evaluates several circuit-based Quantum Machine Learning (QML) models for a binary classification task on the Iris dataset. It provides a direct comparison of different preprocessing strategies (PCA vs. all features) and, most importantly, analyzes the impact of **five distinct variational circuit (ansatz) designs** on model performance.

## 1. Binary Task and Preprocessing

* **Binary Task:** The models are tasked with classifying **Iris Versicolor vs. Iris Virginica**. This is a "hard," non-linearly separable problem, chosen to test the limits of the models' expressibility.
* **Preprocessing:** Two distinct methods are created:
    1.  **Proposal A (Practical):** Applies **PCA** to reduce 4 features to 2, then scales them.
        * **Rationale:** A **practicality-first** design to minimize qubit count, circuit depth, and noise sensitivity for near-term (NISQ) hardware.
    2.  **Proposal B (Expressive):** Uses **all 4 features**, scaled.
        * **Rationale:** An **expressivity-first** design that retains all classical information, relying on the quantum model to find a non-linear separator.

---

## 2. Circuit Architectures and Design Choices

Two distinct quantum architectures (2-qubit and 4-qubit) were created. The 4-qubit architecture was further tested with five different ansatz layers.

### Proposal A: 2-Qubit Architecture

* **Feature Map:** `ZZFeatureMap(feature_dimension=2, reps=2)`. This is a non-linear map that entangles the two input features.
* **Ansatz:** `TwoLocal(num_qubits=2, rotation_blocks='ry', entanglement_blocks='cz', entanglement='linear', reps=3)`. A simple variational circuit with 6 parameters.

### Proposal B: 4-Qubit Architectures (Ansatz Comparison)

All 4-qubit models share a common `PauliFeatureMap(feature_dimension=4, paulis=['Z'])` to encode the 4 features into a $2^4=16$-dimensional space. The key difference is the choice of ansatz (`reps=2` for all):

1.  **`TwoLocal (Circular)`:**
    * **Design:** The "standard" `TwoLocal` from `qmlcircuit1-twolocal.py`. It uses `ry` and `rz` rotation gates (high expressibility) and `cx` (CNOT) entanglers in a `circular` pattern.
2.  **`EfficientSU2`:**
    * **Design:** A well-known, hardware-efficient ansatz. It is very similar to `TwoLocal` and uses `SU(2)` rotations (`ry`, `rz`) and `cx` entanglers.
3.  **`TwoLocal (SCA)`:**
    * **Design:** Uses a more complex "Shifted Circular Alternating" (`sca`) entanglement. This strategy better "mixes" information between all qubits across multiple layers, enhancing expressibility.
4.  **`TwoLocal (RZZ Entangler)`:**
    * **Design:** The **most expressive** ansatz. Instead of a fixed `cx` gate, it uses a **trainable `rzz` gate** for entanglement. This adds more parameters, allowing the model to *learn* the optimal amount of entanglement.
5.  **`RealAmplitudes`:**
    * **Design:** The **least expressive** 4-qubit ansatz. It only uses `ry` rotation gates (not `rz`). This results in fewer parameters and a circuit state with only real amplitudes.

---

## 3. Expressibility and Complex Decision Boundaries

* **Proposal A (2-Qubit):** **Severely limited.** Its ability to find boundaries is capped by the 2D data from PCA. It is "blind" to any complex patterns it was not fed and **cannot** represent the true decision boundary for this problem.
* **Proposal B (4-Qubit):** **High.** All 4-qubit models map the 4D data into a 16D space, which allows them to find a simple separator (a hyperplane) that corresponds to a **highly complex, non-linear decision boundary** in the original 4D space. The *choice* of ansatz (`RealAmplitudes` vs. `RZZ Entangler`) then fine-tunes this expressibility, trading it for trainability.

---

## 4. Performance, Strengths, and Weaknesses

* **Proposal A (2-Qubit):**
    * **Performance:** Fails the non-linear task.
    * **Strength:** Fast, low resource use, and noise-resilient.
    * **Weakness:** The linear PCA preprocessing **destroys the critical information** needed to solve this complex problem.
* **Proposal B (4-Qubit "Bake-Off"):**
    * **Strength:** High expressibility allows them to successfully model the non-linear data.
    * **Weakness:** High resource cost, slow, and poor noise resilience.
    * **`RealAmplitudes`:** (Simplest) Is the **fastest to train** but risks **underfitting** (being too simple to find the boundary).
    * **`RZZ Entangler`:** (Most complex) Has the **most power** but is the **slowest to train** and risks **barren plateaus** or overfitting.

---

## 5. Reasoning and Practical Considerations

1.  **Expressibility vs. Accuracy:** For the non-linear task, high expressibility (4-qubits, complex ansatz) is required for high accuracy. The 2-qubit PCA model failed this task completely.
2.  **Expressibility vs. Trainability:** The `qmlcircuit-other-circuits.py` script highlights the crucial **Expressibility vs. Trainability** trade-off. The `RZZ Entangler` model is the most powerful *in theory*, but its complex, high-parameter landscape may be too difficult for the optimizer to train, potentially leading to a worse result than a "good enough" model like `EfficientSU2`.
3.  **Practicality :** The 2-qubit PCA approach (Proposal A) is **scalable** and **noise-resilient**, making it the only practical choice for NISQ devices. The 4-qubit models (Proposal B) are **not scalable** (1-qubit-per-feature) and would fail on real hardware due to their depth and noise sensitivity.

**Conclusion:** This demonstrates that effective QML requires balancing a model's expressivity (for accuracy) with its complexity (for practical trainability and noise resilience).
