import pytest

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error! Division by zero."
    return a / b

class TestArithmeticOperations:

    def test_add_positive_numbers(self):
        assert add(5, 3) == 8

    def test_add_negative_numbers(self):
        assert add(-5, -3) == -8

    def test_add_mixed_numbers(self):
        assert add(5, -3) == 2

    def test_add_zero(self):
        assert add(5, 0) == 5

    def test_subtract_positive_numbers(self):
        assert subtract(5, 3) == 2

    def test_subtract_negative_numbers(self):
        assert subtract(-5, -3) == -2

    def test_subtract_mixed_numbers(self):
        assert subtract(5, -3) == 8

    def test_subtract_zero(self):
        assert subtract(5, 0) == 5

    def test_multiply_positive_numbers(self):
        assert multiply(5, 3) == 15

    def test_multiply_negative_numbers(self):
        assert multiply(-5, -3) == 15

    def test_multiply_mixed_numbers(self):
        assert multiply(5, -3) == -15

    def test_multiply_zero(self):
        assert multiply(5, 0) == 0

    def test_divide_positive_numbers(self):
        assert divide(15, 3) == 5

    def test_divide_negative_numbers(self):
        assert divide(-15, -3) == 5

    def test_divide_mixed_numbers(self):
        assert divide(15, -3) == -5

    def test_divide_by_zero(self):
        assert divide(15, 0) == "Error! Division by zero."

    def test_divide_zero_by_number(self):
        assert divide(0, 5) == 0.0