import pytest

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

class TestAdd:
    def test_add_positive_numbers(self):
        assert add(2, 3) == 5

    def test_add_negative_numbers(self):
        assert add(-2, -3) == -5

    def test_add_mixed_numbers(self):
        assert add(2, -3) == -1

    def test_add_zero(self):
        assert add(5, 0) == 5

class TestSubtract:
    def test_subtract_positive_numbers(self):
        assert subtract(5, 2) == 3

    def test_subtract_negative_numbers(self):
        assert subtract(-5, -2) == -3

    def test_subtract_mixed_numbers(self):
        assert subtract(2, -3) == 5

    def test_subtract_zero(self):
        assert subtract(5, 0) == 5

    def test_subtract_from_zero(self):
        assert subtract(0, 5) == -5

class TestMultiply:
    def test_multiply_positive_numbers(self):
        assert multiply(2, 3) == 6

    def test_multiply_negative_numbers(self):
        assert multiply(-2, -3) == 6

    def test_multiply_mixed_numbers(self):
        assert multiply(2, -3) == -6

    def test_multiply_by_zero(self):
        assert multiply(5, 0) == 0

    def test_multiply_by_one(self):
        assert multiply(5, 1) == 5

class TestDivide:
    def test_divide_positive_numbers(self):
        assert divide(6, 2) == 3

    def test_divide_negative_numbers(self):
        assert divide(-6, -2) == 3

    def test_divide_mixed_numbers(self):
        assert divide(6, -2) == -3

    def test_divide_by_one(self):
        assert divide(5, 1) == 5

    def test_divide_by_zero(self):
        assert divide(5, 0) == "Error: Cannot divide by zero!"

    def test_divide_zero_by_number(self):
        assert divide(0, 5) == 0