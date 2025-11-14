import pytest

def reverse_string(text):
    return text[::-1]

def word_count(text):
    return len(text.split())

def to_upper(text):
    return text.upper()

def is_even(num):
    return num % 2 == 0

def generate_numbers(start, end):
    return list(range(start, end + 1))

# Pytest test cases
class TestReverseString:
    def test_reverse_normal_string(self):
        assert reverse_string("hello") == "olleh"

    def test_reverse_empty_string(self):
        assert reverse_string("") == ""

    def test_reverse_palindrome(self):
        assert reverse_string("madam") == "madam"

    def test_reverse_string_with_spaces(self):
        assert reverse_string("hello world") == "dlrow olleh"

class TestWordCount:
    def test_word_count_normal_string(self):
        assert word_count("hello world") == 2

    def test_word_count_empty_string(self):
        assert word_count("") == 0

    def test_word_count_string_with_leading_and_trailing_spaces(self):
        assert word_count("  hello world  ") == 2

    def test_word_count_string_with_multiple_spaces(self):
        assert word_count("hello   world") == 2

    def test_word_count_string_with_only_spaces(self):
        assert word_count("   ") == 0

class TestToUpper:
    def test_to_upper_normal_string(self):
        assert to_upper("hello") == "HELLO"

    def test_to_upper_empty_string(self):
        assert to_upper("") == ""

    def test_to_upper_string_with_mixed_case(self):
        assert to_upper("Hello World") == "HELLO WORLD"

    def test_to_upper_string_with_numbers(self):
        assert to_upper("Hello123World") == "HELLO123WORLD"

class TestIsEven:
    def test_is_even_even_number(self):
        assert is_even(4) == True

    def test_is_even_odd_number(self):
        assert is_even(5) == False

    def test_is_even_zero(self):
        assert is_even(0) == True

    def test_is_even_negative_even_number(self):
        assert is_even(-4) == True

    def test_is_even_negative_odd_number(self):
        assert is_even(-5) == False

class TestGenerateNumbers:
    def test_generate_numbers_normal_range(self):
        assert generate_numbers(1, 5) == [1, 2, 3, 4, 5]

    def test_generate_numbers_same_start_and_end(self):
        assert generate_numbers(5, 5) == [5]

    def test_generate_numbers_start_greater_than_end(self):
        assert generate_numbers(5, 1) == []

    def test_generate_numbers_negative_range(self):
        assert generate_numbers(-2, 2) == [-2, -1, 0, 1, 2]

    def test_generate_numbers_negative_start_and_end(self):
        assert generate_numbers(-5, -1) == [-5, -4, -3, -2, -1]