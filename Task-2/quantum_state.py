import numpy as np

def prepare_state_vector(amplitudes):
    """
    Prepares a normalized quantum state vector from a list of amplitudes.

    This function implements the core task and the stretch goal,
    supporting any n-qubit state (where amplitudes list size is 2^n).

    Args:
        amplitudes (list-like): A list, tuple, or array of complex
                                numbers representing the amplitudes
                                of the quantum state.

    Returns:
        np.ndarray: A 1D NumPy array of dtype=complex, representing the
                    normalized state vector.

    Raises:
        ValueError: If the number of amplitudes is not a power of 2,
                    or if the input is a zero vector.
    """
    # Convert to a complex NumPy array
    state_vector = np.array(amplitudes, dtype=complex)
    
    n_amplitudes = state_vector.size
    
    # Check if size is nonempty
    if n_amplitudes == 0:
        raise ValueError("Input amplitudes list cannot be empty.")
        
    # Check if n_amplitudes is a power of 2
    # We can use a bitwise trick or log2
    n_qubits_float = np.log2(n_amplitudes)
    if not np.isclose(n_qubits_float, round(n_qubits_float)):
        raise ValueError(
            f"Number of amplitudes must be a power of 2 (e.g., 2, 4, 8, ...). "
            f"Got {n_amplitudes}."
        )
        
    n_qubits = int(round(n_qubits_float))

    # Normalization Step
    # Calculate the sum of the squared magnitudes
    # np.abs(a + bj) calculates sqrt(a^2 + b^2)
    # So, (np.abs(...))**2 is a^2 + b^2 (or |a_i|^2)
    norm_squared = np.sum(np.abs(state_vector) ** 2)

    # Check for zero vector
    if np.isclose(norm_squared, 0.0):
        raise ValueError("Cannot normalize a zero vector. It is also physically worthless.")

    # Check if the state is already normalized (within floating-point tolerance)
    if not np.isclose(norm_squared, 1.0):
        print(f"Info: Input state for {n_qubits} qubit(s) was not normalized "
              f"(Sum of |a_i|^2 = {norm_squared:.6f}). Normalizing...")
        norm = np.sqrt(norm_squared)
        state_vector = state_vector / norm

    return state_vector

# --- Example Usage ---
if __name__ == "__main__":
    # 2-qubit (Task requirement)
    # An unnormalized state [1, 0, 1, 0]
    # Expected: [1/sqrt(2), 0, 1/sqrt(2), 0]
    unnormalized_2q = [1, 0, 1, 0]
    state_2q = prepare_state_vector(unnormalized_2q)
    print(f"--- 2-Qubit Example ---")
    print(f"Input: {unnormalized_2q}")
    print(f"Normalized State Vector: \n{state_2q}")
    print(f"Sum of |amp|^2: {np.sum(np.abs(state_2q)**2):.2f}\n")

    # Example for 2-qubit with complex numbers
    # Let's use [1+1j, 0, 0, 1-1j]
    # Expected: [ (1+1j)/2, 0, 0, (1-1j)/2 ] = [ 0.5+0.5j, 0, 0, 0.5-0.5j ]
    unnormalized_complex_2q = [1+1j, 0, 0, 1-1j]
    state_complex_2q = prepare_state_vector(unnormalized_complex_2q)
    print(f"--- 2-Qubit Complex Example ---")
    print(f"Input: {unnormalized_complex_2q}")
    print(f"Normalized State Vector: \n{state_complex_2q}")
    print(f"Sum of |amp|^2: {np.sum(np.abs(state_complex_2q)**2):.2f}\n")

    # Example for 3-qubit (Stretch Goal)
    # An unnormalized state of 8 ones
    # Expected: [1/sqrt(8), ..., 1/sqrt(8)]
    unnormalized_3q = [1] * 8  # [1, 1, 1, 1, 1, 1, 1, 1]
    state_3q = prepare_state_vector(unnormalized_3q)
    print(f"--- 3-Qubit Example (Stretch Goal) ---")
    print(f"Input: {unnormalized_3q}")
    print(f"Normalized State Vector: \n{state_3q}")
    print(f"Sum of |amp|^2: {np.sum(np.abs(state_3q)**2):.2f}\n")

    # Example of a failure (not power of 2)
    try:
        prepare_state_vector([1, 2, 3])
    except ValueError as e:
        print(f"--- Failure Example (Dimension) ---")
        print(f"Input: [1, 2, 3]")
        print(f"Caught expected error: {e}\n")

    # Example of a failure (zero vector)
    try:
        prepare_state_vector([0, 0, 0, 0])
    except ValueError as e:
        print(f"--- Failure Example (Zero Vector) ---")
        print(f"Input: [0, 0, 0, 0]")
        print(f"Caught expected error: {e}\n")
