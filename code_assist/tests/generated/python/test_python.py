import math
import pytest

# Copy ALL function implementations at the top
def calculate_square_root(number):
    result = math.sqrt(number)
    return result

# The following lines are part of the original script,
# but not part of the function implementation to be tested.
# value = calculate_square_root(25)
# print("Square root:", value)


# Test cases for calculate_square_root(number)
def test_calculate_square_root_positive_integer_perfect_square():
    """Test with a positive integer that is a perfect square."""
    assert calculate_square_root(25) == 5.0

def test_calculate_square_root_positive_integer_non_perfect_square():
    """Test with a positive integer that is not a perfect square."""
    # Using pytest.approx for floating-point comparisons
    assert calculate_square_root(2) == pytest.approx(1.4142135623730951)

def test_calculate_square_root_positive_float():
    """Test with a positive float number."""
    assert calculate_square_root(9.0) == 3.0

def test_calculate_square_root_zero():
    """Test with zero as input."""
    assert calculate_square_root(0) == 0.0

def test_calculate_square_root_negative_number_raises_value_error():
    """Test that a negative number raises a ValueError."""
    with pytest.raises(ValueError, match="math domain error"):
        calculate_square_root(-4)

def test_calculate_square_root_non_numeric_input_raises_type_error():
    """Test that non-numeric input (e.g., string) raises a TypeError."""
    with pytest.raises(TypeError):
        calculate_square_root("hello")

def test_calculate_square_root_large_positive_number():
    """Test with a large positive number."""
    assert calculate_square_root(1_000_000) == 1000.0