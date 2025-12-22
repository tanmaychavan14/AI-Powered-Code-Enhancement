import pytest

# Python code to analyze (copied for self-containment in test file)
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

# Test cases for add(a, b)
class TestAdd:
    @pytest.mark.parametrize("a, b, expected", [
        (1, 2, 3),         # Positive integers
        (-1, -2, -3),      # Negative integers
        (5, -3, 2),        # Mixed integers
        (0, 100, 100),     # Zero with positive
        (10.5, 2.5, 13.0), # Floats
        (0, 0, 0),         # Zeros
        (-7, 7, 0),        # Opposite numbers
    ])
    def test_add_normal_operation(self, a, b, expected):
        """Test addition with various numbers including positive, negative, and floats."""
        assert add(a, b) == expected

# Test cases for subtract(a, b)
class TestSubtract:
    @pytest.mark.parametrize("a, b, expected", [
        (5, 3, 2),         # Positive integers
        (3, 5, -2),        # Positive integers, result negative
        (-5, -3, -2),      # Negative integers
        (-3, -5, 2),       # Negative integers, result positive
        (10, -5, 15),      # Mixed integers
        (0, 7, -7),        # Subtract from zero
        (7, 0, 7),         # Subtract zero
        (10.5, 2.5, 8.0),  # Floats
        (100, 100, 0),     # Same numbers
    ])
    def test_subtract_normal_operation(self, a, b, expected):
        """Test subtraction with various numbers including positive, negative, and floats."""
        assert subtract(a, b) == expected

# Test cases for multiply(a, b)
class TestMultiply:
    @pytest.mark.parametrize("a, b, expected", [
        (2, 3, 6),         # Positive integers
        (-2, 3, -6),       # Negative with positive
        (2, -3, -6),       # Positive with negative
        (-2, -3, 6),       # Two negatives
        (5, 0, 0),         # Multiply by zero
        (0, 10, 0),        # Zero by number
        (7, 1, 7),         # Multiply by one
        (10.5, 2.0, 21.0), # Floats
        (0.5, 0.5, 0.25),  # Fractional floats
    ])
    def test_multiply_normal_operation(self, a, b, expected):
        """Test multiplication with various numbers including positive, negative, floats, and zero."""
        assert multiply(a, b) == expected

# Test cases for divide(a, b)
class TestDivide:
    @pytest.mark.parametrize("a, b, expected", [
        (6, 2, 3.0),          # Positive integers, exact division
        (7, 2, 3.5),          # Positive integers, float result
        (-6, 2, -3.0),        # Negative numerator
        (6, -2, -3.0),        # Negative denominator
        (-6, -2, 3.0),        # Two negatives
        (0, 5, 0.0),          # Zero numerator
        (10.0, 2.5, 4.0),     # Floats, exact division
        (10, 3, 10/3),        # Floats, non-exact division
        (5, 5, 1.0),          # Division resulting in 1
    ])
    def test_divide_normal_operation(self, a, b, expected):
        """Test division with various numbers, ensuring correct float results."""
        assert divide(a, b) == expected

    def test_divide_by_zero(self):
        """Test the specific error condition for division by zero."""
        assert divide(10, 0) == "Error: Cannot divide by zero!"
        assert divide(-5, 0) == "Error: Cannot divide by zero!"
        assert divide(0, 0) == "Error: Cannot divide by zero!" # Even 0/0 is treated as an error by this specific function