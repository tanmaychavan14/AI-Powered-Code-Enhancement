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

# Test cases for add function
def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-2, -3) == -5

def test_add_positive_and_negative_numbers():
    assert add(5, -2) == 3

def test_add_zero():
    assert add(5, 0) == 5

# Test cases for subtract function
def test_subtract_positive_numbers():
    assert subtract(5, 2) == 3

def test_subtract_negative_numbers():
    assert subtract(-2, -3) == 1

def test_subtract_positive_and_negative_numbers():
    assert subtract(5, -2) == 7

def test_subtract_zero():
    assert subtract(5, 0) == 5

# Test cases for multiply function
def test_multiply_positive_numbers():
    assert multiply(2, 3) == 6

def test_multiply_negative_numbers():
    assert multiply(-2, -3) == 6

def test_multiply_positive_and_negative_numbers():
    assert multiply(5, -2) == -10

def test_multiply_zero():
    assert multiply(5, 0) == 0

# Test cases for divide function
def test_divide_positive_numbers():
    assert divide(6, 2) == 3

def test_divide_negative_numbers():
    assert divide(-6, -2) == 3

def test_divide_positive_and_negative_numbers():
    assert divide(6, -2) == -3

def test_divide_by_zero():
    assert divide(5, 0) == "Error! Division by zero."

def test_divide_fractional_result():
    assert divide(5, 2) == 2.5