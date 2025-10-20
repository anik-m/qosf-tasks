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
## Task-4

# ⚛️ Quantum Machine Learning for Iris Classification

This task designs and evaluates distinct Variational Quantum Classifier (VQC) models to solve a binary classification task on the Iris dataset, addressing all requirements outlined.

---

## 1. Proposals, Preprocessing, & Design Rationale

Two distinct models were created to classify the Iris dataset. The primary task chosen was **Versicolor vs. Virginica**, a "hard," non-linearly separable problem, to test the models' limits.

### Proposal A: The 2-Qubit "Practical" Model
* **Preprocessing:** Applies **PCA** to reduce 4 features to 2, then scales them to $[0, \pi]$.
* **Rationale:** This is a **practicality-first** design. It minimizes qubit count (2) and circuit depth, making the model faster and more **noise-resilient** for current hardware.
* **Circuit Design:** Uses a 2-qubit `ZZFeatureMap` (a non-linear map) and a `TwoLocal` ansatz.

### Proposal B: The 4-Qubit "Expressive" Model
* **Preprocessing:** Uses all 4 original features, scaled to $[0, \pi]$. No reduction is performed.
* **Rationale:** This is an **expressivity-first** design. It retains all classical information, mapping the 4D data into a $2^4 = 16$-dimensional quantum feature space to find a non-linear separator.
* **Circuit Design:** Uses a 4-qubit `PauliFeatureMap`. The scripts explore multiple ansatze for this 4-qubit space, including `TwoLocal`, `EfficientSU2`, `RealAmplitudes`, and a `TwoLocal` with trainable `RZZ` entanglers.

---

## 2. Expressibility & Complex Decision Boundaries

* **Proposal A (2-Qubit):** **Severely limited.** Its expressibility is capped by the 2D data from PCA. It is "blind" to any complex, non-linear patterns from the original 4D space and **cannot represent** decision boundaries that rely on discarded features.
* **Proposal B (4-Qubit):** **High.** The 4-qubit architecture operates in a 16D space. This allows it to find a simple separator in the high-dimensional space that corresponds to a **highly complex, non-linear decision boundary** in the original 4D feature space. The "bake-off" script explores the impact of different ansatz choices on this expressibility.

---

## 3. Performance, Strengths, & Weaknesses


For the **Versicolor vs. Virginica** task:

* **Proposal A (2-Qubit):**
    * **Strength:** Fast, efficient, and noise-resilient.
    * **Weakness:** **Fails the task.** The linear PCA preprocessing **destroys the critical information** needed to solve this non-linear problem.

* **Proposal B (4-Qubit):**
    * **Strength:** High expressibility allows it to **successfully find the non-linear boundary** and solve the problem (as seen in both scripts).
    * **Weakness:** Slow, computationally expensive, and highly susceptible to noise.

---

## 4. Reasoning & Practical Considerations

1.  **Expressibility & Accuracy:** The results show expressibility **must match problem complexity**. The 2-qubit model's low expressibility was insufficient for the non-linear task. The 4-qubit models, with their high-dimensional workspace, were required for high accuracy.
2.  **Scalability:** Proposal A's *approach* (compressing features) is highly scalable. Proposal B's 1-qubit-per-feature design is **not scalable**.
3.  **Circuit Depth & Noise Resilience:** Proposal A is shallow and **noise-resilient**, making it the only practical choice for current NISQ hardware. Proposal B's models are deep, slow, and highly **susceptible to noise**.

**Conclusion:** This project highlights the core QML trade-off: **Proposal B is the most *accurate***, but **Proposal A is the most *practical***. Effective QML requires balancing a model's expressivity (for accuracy) with the severe limitations (noise, depth) of current quantum hardware.
