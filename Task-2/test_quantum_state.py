import pytest
import numpy as np
from quantum_state import prepare_state_vector

def test_normalization_is_enforced_2q():
    """Tests that a 2-qubit unnormalized state is correctly normalized."""
    unnormalized = [1, 1, 1, 1]
    expected = np.array([0.5, 0.5, 0.5, 0.5])
    result = prepare_state_vector(unnormalized)
    
    assert result.shape == (4,)
    assert np.allclose(result, expected)
    assert np.isclose(np.sum(np.abs(result)**2), 1.0)

def test_normalization_is_enforced_complex_2q():
    """Tests normalization with complex amplitudes."""
    unnormalized = [1+1j, 0, 1j, 1]
    expected = np.array([(1+1j)/2, 0, 1j/2, 0.5], dtype=complex)
    result = prepare_state_vector(unnormalized)

    assert result.shape == (4,)
    assert np.allclose(result, expected)
    assert np.isclose(np.sum(np.abs(result)**2), 1.0)

def test_output_dimension_is_correct_2q():
    """Checks that the output vector has the correct dimension (4)."""
    bell_state = [1/np.sqrt(2), 0, 0, 1/np.sqrt(2)]
    result = prepare_state_vector(bell_state)
    
    assert result.shape == (4,)
    assert result.dtype == np.complex128 or result.dtype == np.complex64


def test_4_dimension_is_maintained():
    """Checks that the output vector has the correct dimension (4)."""
    bell_state = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    result = prepare_state_vector(bell_state)
    
    assert result.shape == (16,)
    assert result.dtype == np.complex128 or result.dtype == np.complex64

def test_already_normalized_state_unchanged():
    """Tests that an already normalized state is not modified."""
    ghz_state = [1/np.sqrt(2), 0, 0, 1/np.sqrt(2)]
    # Convert to complex type to match function's output type
    expected = np.array(ghz_state, dtype=complex)
    result = prepare_state_vector(ghz_state)
    
    # np.allclose checks for element-wise equality within a tolerance
    assert np.allclose(result, expected)
    assert np.isclose(np.sum(np.abs(result)**2), 1.0)

def test_stretch_goal_3_qubit():
    """Tests the stretch goal for a 3-qubit state (8 amplitudes)."""
    # Input: 8 ones. Norm-sq = 8. Norm = sqrt(8).
    unnormalized = [1] * 8
    expected_val = 1 / np.sqrt(8)
    expected_vec = np.full(8, expected_val, dtype=complex)
    
    result = prepare_state_vector(unnormalized)
    
    assert result.shape == (8,)
    assert np.allclose(result, expected_vec)
    assert np.isclose(np.sum(np.abs(result)**2), 1.0)

def test_failure_on_wrong_dimension():
    """Tests that the function fails if the dimension is not a power of 2."""
    with pytest.raises(ValueError, match="Number of amplitudes must be a power of 2"):
        prepare_state_vector([1, 2, 3]) # 3 amplitudes
        
    with pytest.raises(ValueError, match="Number of amplitudes must be a power of 2"):
        prepare_state_vector([1, 1, 1, 1, 1]) # 5 amplitudes

def test_failure_on_zero_vector():
    """Tests that the function fails if given a zero vector."""
    with pytest.raises(ValueError, match="Cannot normalize a zero vector"):
        prepare_state_vector([0, 0, 0, 0])
        
    with pytest.raises(ValueError, match="Cannot normalize a zero vector"):
        prepare_state_vector([0] * 8) # 3-qubit zero vector

def test_failure_on_empty_list():
    """Tests that the function fails if given an empty list."""
    with pytest.raises(ValueError, match="Input amplitudes list cannot be empty"):
        prepare_state_vector([])
