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


# Pytest test cases start here

import pytest

# --- Tests for reverse_string(text) ---

def test_reverse_string_normal():
    """Test with a standard multi-word string."""
    assert reverse_string("Hello World") == "dlroW olleH"

def test_reverse_string_single_word():
    """Test with a single word string."""
    assert reverse_string("Python") == "nohtyP"

def test_reverse_string_empty():
    """Test with an empty string."""
    assert reverse_string("") == ""

def test_reverse_string_palindrome():
    """Test with a string that is a palindrome."""
    assert reverse_string("madam") == "madam"

def test_reverse_string_with_numbers_and_special_chars():
    """Test with a string containing numbers and special characters."""
    assert reverse_string("123!@#abc") == "cba#@!321"

# --- Tests for word_count(text) ---

def test_word_count_multiple_words():
    """Test with a standard string containing multiple words."""
    assert word_count("This is a test sentence") == 5

def test_word_count_single_word():
    """Test with a string containing only one word."""
    assert word_count("word") == 1

def test_word_count_empty_string():
    """Test with an empty string."""
    assert word_count("") == 0

def test_word_count_only_spaces():
    """Test with a string consisting only of spaces."""
    assert word_count("   ") == 0

def test_word_count_with_leading_trailing_multiple_spaces():
    """Test with extra spaces between words and at ends."""
    assert word_count("  hello   world   python  ") == 3

def test_word_count_with_punctuation():
    """Test with punctuation that is part of words."""
    assert word_count("Hello, world! How are you?") == 5 # "Hello,", "world!", "How", "are", "you?"

# --- Tests for to_upper(text) ---

def test_to_upper_lowercase_string():
    """Test converting a fully lowercase string to uppercase."""
    assert to_upper("hello world") == "HELLO WORLD"

def test_to_upper_mixed_case_string():
    """Test converting a mixed-case string to uppercase."""
    assert to_upper("PyThOn Is FuN") == "PYTHON IS FUN"

def test_to_upper_already_uppercase_string():
    """Test with a string already in uppercase."""
    assert to_upper("HELLO") == "HELLO"

def test_to_upper_empty_string():
    """Test with an empty string."""
    assert to_upper("") == ""

def test_to_upper_with_numbers_and_special_chars():
    """Test with a string containing numbers and special characters."""
    assert to_upper("123!@#abc") == "123!@#ABC"

# --- Tests for is_even(num) ---

def test_is_even_positive_even():
    """Test a positive even number."""
    assert is_even(4) is True

def test_is_even_positive_odd():
    """Test a positive odd number."""
    assert is_even(7) is False

def test_is_even_zero():
    """Test zero, which is considered even."""
    assert is_even(0) is True

def test_is_even_negative_even():
    """Test a negative even number."""
    assert is_even(-2) is True

def test_is_even_negative_odd():
    """Test a negative odd number."""
    assert is_even(-5) is False

# --- Tests for generate_numbers(start, end) ---

def test_generate_numbers_positive_range():
    """Test a standard positive range."""
    assert generate_numbers(1, 5) == [1, 2, 3, 4, 5]

def test_generate_numbers_single_number_range():
    """Test when start and end are the same."""
    assert generate_numbers(7, 7) == [7]

def test_generate_numbers_empty_range():
    """Test when start is greater than end, resulting in an empty list."""
    assert generate_numbers(5, 1) == []

def test_generate_numbers_range_with_negative_numbers():
    """Test a range that includes negative numbers."""
    assert generate_numbers(-3, 1) == [-3, -2, -1, 0, 1]

def test_generate_numbers_range_crossing_zero():
    """Test a range that crosses the zero mark."""
    assert generate_numbers(-2, 2) == [-2, -1, 0, 1, 2]

def test_generate_numbers_large_range():
    """Test a moderately large range to ensure performance/correctness."""
    expected = list(range(0, 101))
    assert generate_numbers(0, 100) == expected