import pytest

# Copy ALL function implementations at the top
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error: Cannot divide by zero!"
    return a / b

def is_even(n):
    if n % 2 == 0:
        return True


# Test cases for add(a, b)
@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),             # Positive integers
    (-1, -2, -3),          # Negative integers
    (5, -3, 2),            # Mixed integers
    (0, 7, 7),             # Addition with zero
    (10.5, 2.3, 12.8),     # Floating point numbers
    (-4.0, 1.5, -2.5),     # Mixed float and negative
    (1000000, 1, 1000001)  # Large numbers
])
def test_add_various_inputs(a, b, expected):
    """Test add function with various integer and float combinations."""
    assert add(a, b) == expected
    assert isinstance(add(a, b), (int, float))

# Test cases for subtract(a, b)
@pytest.mark.parametrize("a, b, expected", [
    (5, 2, 3),             # Positive integers
    (2, 5, -3),            # Result is negative
    (-5, -2, -3),          # Negative integers
    (10, -5, 15),          # Subtracting a negative
    (7, 0, 7),             # Subtraction with zero
    (10.5, 2.5, 8.0),      # Floating point numbers
    (-3.0, 1.5, -4.5)      # Mixed float and negative
])
def test_subtract_various_inputs(a, b, expected):
    """Test subtract function with various integer and float combinations."""
    assert subtract(a, b) == expected
    assert isinstance(subtract(a, b), (int, float))

# Test cases for multiply(a, b)
@pytest.mark.parametrize("a, b, expected", [
    (3, 4, 12),            # Positive integers
    (-3, 4, -12),          # Positive and negative
    (-3, -4, 12),          # Two negative integers
    (5, 0, 0),             # Multiplication by zero
    (1, 7, 7),             # Multiplication by one
    (2.5, 2, 5.0),         # Floating point and integer
    (0.5, 0.5, 0.25)       # Two floating point numbers
])
def test_multiply_various_inputs(a, b, expected):
    """Test multiply function with various integer and float combinations."""
    assert multiply(a, b) == expected
    assert isinstance(multiply(a, b), (int, float))


# Test cases for divide(a, b)
@pytest.mark.parametrize("a, b, expected", [
    (10, 2, 5.0),                      # Positive integers
    (10, 3, 10/3),                     # Division resulting in float
    (-10, 2, -5.0),                    # Negative numerator
    (10, -2, -5.0),                    # Negative denominator
    (0, 5, 0.0),                       # Zero numerator
    (7.5, 2.5, 3.0),                   # Floating point numbers
])
def test_divide_valid_inputs(a, b, expected):
    """Test divide function with valid inputs."""
    assert divide(a, b) == expected
    assert isinstance(divide(a, b), float)

def test_divide_by_zero():
    """Test divide function when dividing by zero."""
    assert divide(10, 0) == "Error: Cannot divide by zero!"
    assert isinstance(divide(10, 0), str)

# Test cases for is_even(n)
@pytest.mark.parametrize("n, expected", [
    (2, True),            # Positive even
    (0, True),            # Zero is even
    (-4, True),           # Negative even
    (2.0, True),          # Even float
])
def test_is_even_returns_true(n, expected):
    """Test is_even for numbers that are explicitly even."""
    assert is_even(n) == expected
    assert isinstance(is_even(n), bool)

@pytest.mark.parametrize("n, expected", [
    (1, None),            # Positive odd
    (-3, None),           # Negative odd
    (2.5, None),          # Odd float (2.5 % 2 is not 0)
    (0.0001, None)        # Very small number, not even
])
def test_is_even_returns_none(n, expected):
    """Test is_even for numbers that are odd, expecting None."""
    assert is_even(n) is expected # Use 'is' for None comparison
    assert is_even(n) is None # Explicitly assert it's None

def test_is_even_non_integer_type_behavior():
    """
    Test behavior of is_even with non-integer inputs.
    The original function does not explicitly handle non-numeric types,
    so a TypeError is expected if a non-numeric type is passed that
    doesn't support the modulo operator.
    """
    with pytest.raises(TypeError):
        is_even("hello")
    with pytest.raises(TypeError):
        is_even([1, 2])