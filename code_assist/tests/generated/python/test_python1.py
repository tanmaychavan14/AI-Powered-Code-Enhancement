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

import pytest

class TestArithmeticFunctions:
    """
    Comprehensive test cases for basic arithmetic functions: add, subtract, multiply, divide.
    """

    # --- Test cases for add(a, b) ---
    def test_add_positive_integers(self):
        """Test addition with two positive integers."""
        assert add(5, 3) == 8

    def test_add_negative_integers(self):
        """Test addition with two negative integers."""
        assert add(-5, -3) == -8

    def test_add_mixed_integers(self):
        """Test addition with a positive and a negative integer."""
        assert add(10, -7) == 3

    def test_add_with_zero(self):
        """Test addition where one of the operands is zero."""
        assert add(0, 15) == 15
        assert add(-10, 0) == -10

    def test_add_float_numbers(self):
        """Test addition with floating-point numbers."""
        assert add(2.5, 3.5) == 6.0
        assert add(1.1, 2.2) == pytest.approx(3.3) # Use pytest.approx for float comparison

    # --- Test cases for subtract(a, b) ---
    def test_subtract_positive_integers(self):
        """Test subtraction with two positive integers."""
        assert subtract(10, 5) == 5

    def test_subtract_negative_integers(self):
        """Test subtraction with two negative integers."""
        assert subtract(-10, -5) == -5

    def test_subtract_mixed_integers(self):
        """Test subtraction where the first operand is positive and the second is negative."""
        assert subtract(10, -5) == 15
        """Test subtraction where the first operand is negative and the second is positive."""
        assert subtract(-10, 5) == -15

    def test_subtract_to_zero(self):
        """Test subtraction resulting in zero."""
        assert subtract(7, 7) == 0

    def test_subtract_float_numbers(self):
        """Test subtraction with floating-point numbers."""
        assert subtract(10.5, 3.2) == pytest.approx(7.3)
        assert subtract(5.0, 5.0) == 0.0

    # --- Test cases for multiply(a, b) ---
    def test_multiply_positive_integers(self):
        """Test multiplication with two positive integers."""
        assert multiply(4, 3) == 12

    def test_multiply_negative_integers(self):
        """Test multiplication with two negative integers."""
        assert multiply(-4, -3) == 12

    def test_multiply_mixed_integers(self):
        """Test multiplication with a positive and a negative integer."""
        assert multiply(4, -3) == -12
        assert multiply(-4, 3) == -12

    def test_multiply_by_zero(self):
        """Test multiplication where one of the operands is zero."""
        assert multiply(0, 9) == 0
        assert multiply(15, 0) == 0
        assert multiply(0.5, 0) == 0.0

    def test_multiply_float_numbers(self):
        """Test multiplication with floating-point numbers."""
        assert multiply(2.5, 2) == 5.0
        assert multiply(1.5, 2.0) == 3.0

    # --- Test cases for divide(a, b) ---
    def test_divide_positive_integers(self):
        """Test division with two positive integers, exact division."""
        assert divide(10, 2) == 5.0

    def test_divide_positive_integers_float_result(self):
        """Test division with two positive integers, resulting in a float."""
        assert divide(7, 2) == 3.5

    def test_divide_negative_and_positive_integers(self):
        """Test division with a negative numerator and a positive denominator."""
        assert divide(-10, 2) == -5.0
        """Test division with a positive numerator and a negative denominator."""
        assert divide(10, -2) == -5.0

    def test_divide_by_zero_error_message(self):
        """Test division by zero, expecting the specific error string."""
        assert divide(10, 0) == "Error: Cannot divide by zero!"
        assert divide(-5, 0) == "Error: Cannot divide by zero!"
        assert divide(0.0, 0) == "Error: Cannot divide by zero!"

    def test_divide_zero_by_non_zero(self):
        """Test division of zero by a non-zero number."""
        assert divide(0, 5) == 0.0
        assert divide(0.0, 100) == 0.0

    def test_divide_float_numbers(self):
        """Test division with floating-point numbers."""
        assert divide(7.5, 2.5) == 3.0
        assert divide(10.0, 3.0) == pytest.approx(3.3333333333333335)