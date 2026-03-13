# --- Original Python Code (copied as per rules) ---
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
# --- End of Original Python Code ---

# Pytest test cases

def test_add_positive_integers():
    """Test addition of two positive integers."""
    assert add(2, 3) == 5

def test_add_negative_integers():
    """Test addition of two negative integers."""
    assert add(-5, -10) == -15

def test_add_mixed_integers():
    """Test addition of a positive and a negative integer."""
    assert add(10, -3) == 7
    assert add(-7, 2) == -5

def test_add_floats():
    """Test addition of floating-point numbers."""
    assert add(2.5, 3.5) == 6.0
    assert add(-1.5, 0.5) == -1.0

def test_add_with_zero():
    """Test addition with zero."""
    assert add(0, 5) == 5
    assert add(-8, 0) == -8

def test_subtract_positive_integers_positive_result():
    """Test subtraction of positive integers resulting in a positive number."""
    assert subtract(10, 3) == 7

def test_subtract_positive_integers_negative_result():
    """Test subtraction of positive integers resulting in a negative number."""
    assert subtract(3, 10) == -7

def test_subtract_negative_integers():
    """Test subtraction involving negative integers."""
    assert subtract(-5, -2) == -3
    assert subtract(-2, -5) == 3

def test_subtract_with_zero():
    """Test subtraction with zero."""
    assert subtract(5, 0) == 5
    assert subtract(0, 5) == -5
    assert subtract(0, -5) == 5

def test_subtract_floats():
    """Test subtraction of floating-point numbers."""
    assert subtract(7.5, 2.5) == 5.0
    assert subtract(2.0, 5.5) == -3.5

def test_multiply_positive_integers():
    """Test multiplication of two positive integers."""
    assert multiply(4, 5) == 20

def test_multiply_negative_integers():
    """Test multiplication of two negative integers."""
    assert multiply(-3, -6) == 18

def test_multiply_mixed_integers():
    """Test multiplication of a positive and a negative integer."""
    assert multiply(7, -2) == -14
    assert multiply(-5, 4) == -20

def test_multiply_by_zero():
    """Test multiplication by zero."""
    assert multiply(10, 0) == 0
    assert multiply(-5, 0) == 0
    assert multiply(0, 0) == 0

def test_multiply_floats():
    """Test multiplication of floating-point numbers."""
    assert multiply(2.5, 2.0) == 5.0
    assert multiply(1.5, -3.0) == -4.5

def test_divide_positive_integers():
    """Test division of two positive integers."""
    assert divide(10, 2) == 5.0

def test_divide_negative_integers():
    """Test division involving negative integers."""
    assert divide(-10, 2) == -5.0
    assert divide(10, -2) == -5.0
    assert divide(-10, -2) == 5.0

def test_divide_by_one():
    """Test division by one."""
    assert divide(7, 1) == 7.0
    assert divide(-7, 1) == -7.0

def test_divide_floats():
    """Test division resulting in a float or with float inputs."""
    assert divide(10, 4) == 2.5
    assert divide(7.5, 2.5) == 3.0

def test_divide_by_zero_error_message():
    """Test division by zero returns the specific error string."""
    assert divide(10, 0) == "Error: Cannot divide by zero!"
    assert divide(-5, 0) == "Error: Cannot divide by zero!"
    assert divide(0, 0) == "Error: Cannot divide by zero!"

def test_is_even_positive_even():
    """Test a positive even number."""
    assert is_even(4) is True

def test_is_even_negative_even():
    """Test a negative even number."""
    assert is_even(-6) is True

def test_is_even_zero():
    """Test zero, which is considered even."""
    assert is_even(0) is True

def test_is_even_positive_odd():
    """Test a positive odd number, expecting None."""
    assert is_even(3) is None

def test_is_even_negative_odd():
    """Test a negative odd number, expecting None."""
    assert is_even(-7) is None