import math
import pytest

# Copy ALL function implementations at the top
def calculate_square_root(number):
    result = math.sqrt(number)
    return result

# No need to test the global variable assignment or print statement.
# Only functions are to be tested.

# Test cases for calculate_square_root(number)
def test_calculate_square_root_positive_integer():
    """Test with a positive integer perfect square."""
    assert calculate_square_root(25) == 5.0
    assert isinstance(calculate_square_root(25), float)

def test_calculate_square_root_positive_float():
    """Test with a positive float number."""
    assert calculate_square_root(9.0) == 3.0
    assert isinstance(calculate_square_root(9.0), float)

def test_calculate_square_root_zero():
    """Test with zero."""
    assert calculate_square_root(0) == 0.0
    assert isinstance(calculate_square_root(0), float)

def test_calculate_square_root_one():
    """Test with one."""
    assert calculate_square_root(1) == 1.0
    assert isinstance(calculate_square_root(1), float)

def test_calculate_square_root_non_perfect_square():
    """Test with a non-perfect square, checking for approximate value."""
    expected_value = 1.4142135623730951
    assert calculate_square_root(2) == pytest.approx(expected_value)
    assert isinstance(calculate_square_root(2), float)

def test_calculate_square_root_large_number():
    """Test with a large number."""
    assert calculate_square_root(1000000) == 1000.0
    assert isinstance(calculate_square_root(1000000), float)

def test_calculate_square_root_negative_number_raises_value_error():
    """Test that a negative number raises a ValueError."""
    with pytest.raises(ValueError, match="math domain error"):
        calculate_square_root(-9)

def test_calculate_square_root_non_numeric_input_raises_type_error():
    """Test that a non-numeric input (string) raises a TypeError."""
    with pytest.raises(TypeError):
        calculate_square_root("hello")

def test_calculate_square_root_list_input_raises_type_error():
    """Test that a non-numeric input (list) raises a TypeError."""
    with pytest.raises(TypeError):
        calculate_square_root([4])

def test_calculate_square_root_complex_number_raises_type_error():
    """Test that a complex number raises a TypeError."""
    with pytest.raises(TypeError):
        calculate_square_root(2 + 3j)