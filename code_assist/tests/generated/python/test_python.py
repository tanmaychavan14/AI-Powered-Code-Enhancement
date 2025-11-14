import pytest

# Test cases for reverse_string function
def test_reverse_string_normal():
    assert reverse_string("hello") == "olleh"

def test_reverse_string_empty():
    assert reverse_string("") == ""

def test_reverse_string_palindrome():
    assert reverse_string("madam") == "madam"

def test_reverse_string_with_spaces():
    assert reverse_string("hello world") == "dlrow olleh"

# Test cases for word_count function
def test_word_count_normal():
    assert word_count("hello world") == 2

def test_word_count_empty():
    assert word_count("") == 0

def test_word_count_multiple_spaces():
    assert word_count(" hello   world ") == 3

def test_word_count_single_word():
    assert word_count("hello") == 1

# Test cases for to_upper function
def test_to_upper_normal():
    assert to_upper("hello") == "HELLO"

def test_to_upper_empty():
    assert to_upper("") == ""

def test_to_upper_mixed_case():
    assert to_upper("Hello World") == "HELLO WORLD"

def test_to_upper_already_upper():
    assert to_upper("HELLO") == "HELLO"

# Test cases for is_even function
def test_is_even_even():
    assert is_even(4) == True

def test_is_even_odd():
    assert is_even(5) == False

def test_is_even_zero():
    assert is_even(0) == True

def test_is_even_negative_even():
    assert is_even(-4) == True

def test_is_even_negative_odd():
    assert is_even(-5) == False

# Test cases for generate_numbers function
def test_generate_numbers_normal():
    assert generate_numbers(1, 5) == [1, 2, 3, 4, 5]

def test_generate_numbers_same_start_end():
    assert generate_numbers(5, 5) == [5]

def test_generate_numbers_start_greater_than_end():
    assert generate_numbers(5, 1) == []

def test_generate_numbers_negative_start_end():
    assert generate_numbers(-2, 2) == [-2, -1, 0, 1, 2]

def test_generate_numbers_negative_range():
    assert generate_numbers(-5, -1) == [-5, -4, -3, -2, -1]

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