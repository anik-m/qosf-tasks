from quantum_state import prepare_state_vector
import numpy as np

def run_interactive_test():
    """
    Runs an interactive command-line session to test n-qubit state preparation.
    """
    print("--- Interactive N-Qubit State Vector Test ---")
    
    while True:
        # 1. Get the number of qubits from the user
        try:
            n_qubits_str = input("\nEnter the number of qubits (n): ")
            if not n_qubits_str:
                print("Exiting.")
                break
            n_qubits = int(n_qubits_str)
            if n_qubits <= 0:
                print("Error: Number of qubits must be a positive integer.")
                continue
        except ValueError:
            print("Error: Please enter a valid integer.")
            continue
            
        num_amplitudes = 2**n_qubits
        print(f"An {n_qubits}-qubit state requires {num_amplitudes} amplitudes.")
        print("Enter the amplitudes below. For complex numbers, use 'j' (e.g., '3+4j').")

        # 2. Collect the amplitudes
        amplitudes = []
        for i in range(num_amplitudes):
            while True:
                try:
                    # Basis state label, e.g., |001> for i=1 in a 3-qubit system
                    basis_state = format(i, f'0{n_qubits}b')
                    amp_str = input(f"  Enter amplitude for |{basis_state}>: ")
                    # Use complex() to parse the string into a complex number
                    amplitudes.append(complex(amp_str))
                    break
                except ValueError:
                    print("    Invalid input. Please enter a valid number (e.g., '5', '-1.2', or '3+4j').")
        
        # 3. Call the preparation function and handle outcomes
        try:
            print("\nProcessing amplitudes:", [str(a) for a in amplitudes])
            normalized_vector = prepare_state_vector(amplitudes)
            
            print("\n✅ Success! Normalized State Vector:")
            # Use numpy's print options for better formatting
            with np.printoptions(precision=6, suppress=True):
                print(normalized_vector)
            
            # Final check of the norm
            final_norm_sq = np.sum(np.abs(normalized_vector)**2)
            print(f"Final sum of squared magnitudes: {final_norm_sq:.6f}")

        except ValueError as e:
            print(f"\n❌ Error: {e}")
        
        # 4. Ask to continue
        another_test = input("\nRun another test? (y/n, default is y): ").lower().strip()
        if another_test == 'n':
            print("Exiting.")
            break

if __name__ == "__main__":
    run_interactive_test()
