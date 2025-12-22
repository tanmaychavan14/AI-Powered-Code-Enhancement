# Example Python functions with different operations

# Reverse a string
def reverse_string(text):
    return text[::-1]

# Count words in a string
def word_count(text):
    return len(text.split())

# Convert string to uppercase
def to_upper(text):
    return text.upper()

# Check if a number is even
def is_even(num):
    return num % 2 == 0

# Generate a list of numbers from start to end
def generate_numbers(start, end):
    return list(range(start, end + 1))

import pytest

# Test cases for reverse_string(text)
def test_reverse_string_normal_text():
    """Tests normal text reversal."""
    assert reverse_string("hello") == "olleh"
    assert reverse_string("Python Programming") == "gnimmargorP nohtyP"

def test_reverse_string_with_empty_string():
    """Tests reversal of an empty string."""
    assert reverse_string("") == ""

def test_reverse_string_with_special_characters_and_numbers():
    """Tests reversal with mixed characters and numbers."""
    assert reverse_string("123!@#abc") == "cba#@!321"
    assert reverse_string("racecar!") == "!racecar" # Case sensitive reversal

def test_reverse_string_with_leading_trailing_spaces():
    """Tests reversal when string has leading/trailing spaces."""
    assert reverse_string("  hello world  ") == "  dlrow olleh  "

def test_reverse_string_type_error_with_non_string():
    """Tests if TypeError is raised for non-string input."""
    with pytest.raises(TypeError):
        reverse_string(12345)
    with pytest.raises(TypeError):
        reverse_string(['a', 'b', 'c'])

# Test cases for word_count(text)
def test_word_count_single_word():
    """Tests counting a single word."""
    assert word_count("hello") == 1

def test_word_count_multiple_words():
    """Tests counting multiple words separated by single spaces."""
    assert word_count("hello world") == 2
    assert word_count("this is a test sentence") == 5

def test_word_count_with_extra_spaces():
    """Tests counting words with multiple spaces between them or leading/trailing spaces."""
    assert word_count("  hello   world  ") == 2
    assert word_count("   only   a   few   words   ") == 4

def test_word_count_empty_string():
    """Tests counting words in an empty string."""
    assert word_count("") == 0

def test_word_count_only_whitespace():
    """Tests counting words in a string consisting only of whitespace."""
    assert word_count("   \t\n  ") == 0

def test_word_count_type_error_with_non_string():
    """Tests if AttributeError is raised for non-string input."""
    with pytest.raises(AttributeError): # .split() is a string method
        word_count(123)
    with pytest.raises(AttributeError):
        word_count(None)

# Test cases for to_upper(text)
def test_to_upper_mixed_case():
    """Tests conversion of a mixed-case string to uppercase."""
    assert to_upper("Hello World") == "HELLO WORLD"
    assert to_upper("pyTest Framework") == "PYTEST FRAMEWORK"

def test_to_upper_all_lowercase():
    """Tests conversion of an all-lowercase string."""
    assert to_upper("hello") == "HELLO"
    assert to_upper("python") == "PYTHON"

def test_to_upper_all_uppercase():
    """Tests conversion of an already uppercase string (should remain unchanged)."""
    assert to_upper("UPPERCASE") == "UPPERCASE"

def test_to_upper_empty_string():
    """Tests conversion of an empty string."""
    assert to_upper("") == ""

def test_to_upper_with_numbers_and_symbols():
    """Tests conversion of string with numbers and symbols."""
    assert to_upper("123!@#Abc") == "123!@#ABC"
    assert to_upper("SPECIAL-CHARS-123") == "SPECIAL-CHARS-123"

def test_to_upper_type_error_with_non_string():
    """Tests if AttributeError is raised for non-string input."""
    with pytest.raises(AttributeError): # .upper() is a string method
        to_upper(456)
    with pytest.raises(AttributeError):
        to_upper([1, 2, 3])

# Test cases for is_even(num)
def test_is_even_positive_even():
    """Tests positive even numbers."""
    assert is_even(4) is True
    assert is_even(100) is True

def test_is_even_positive_odd():
    """Tests positive odd numbers."""
    assert is_even(5) is False
    assert is_even(99) is False

def test_is_even_zero():
    """Tests if zero is considered even."""
    assert is_even(0) is True

def test_is_even_negative_numbers():
    """Tests negative even and odd numbers."""
    assert is_even(-2) is True
    assert is_even(-7) is False

def test_is_even_float_numbers():
    """Tests float numbers (Python's % operator works for floats)."""
    assert is_even(4.0) is True
    assert is_even(3.5) is False
    assert is_even(-6.0) is True

def test_is_even_type_error_with_non_numeric():
    """Tests if TypeError is raised for non-numeric input."""
    with pytest.raises(TypeError): # % operator not supported for string
        is_even("abc")
    with pytest.raises(TypeError):
        is_even(None)
    with pytest.raises(TypeError):
        is_even([2])

# Test cases for generate_numbers(start, end)
def test_generate_numbers_positive_range():
    """Tests generating a list of positive numbers."""
    assert generate_numbers(1, 5) == [1, 2, 3, 4, 5]
    assert generate_numbers(10, 12) == [10, 11, 12]

def test_generate_numbers_single_number_range():
    """Tests generating a list for start == end."""
    assert generate_numbers(5, 5) == [5]
    assert generate_numbers(0, 0) == [0]

def test_generate_numbers_negative_range():
    """Tests generating a list of negative numbers."""
    assert generate_numbers(-3, 0) == [-3, -2, -1, 0]
    assert generate_numbers(-5, -3) == [-5, -4, -3]

def test_generate_numbers_start_greater_than_end():
    """Tests scenario where start is greater than end (should return empty list)."""
    assert generate_numbers(5, 1) == []
    assert generate_numbers(10, -5) == []

def test_generate_numbers_mixed_positive_negative_range():
    """Tests a range spanning positive and negative numbers including zero."""
    assert generate_numbers(-1, 1) == [-1, 0, 1]

def test_generate_numbers_type_error_with_non_integer():
    """Tests if TypeError is raised for non-integer start/end."""
    with pytest.raises(TypeError): # range expects integers
        generate_numbers("a", 5)
    with pytest.raises(TypeError):
        generate_numbers(1, "b")
    with pytest.raises(TypeError):
        generate_numbers(1.5, 5) # range expects integers