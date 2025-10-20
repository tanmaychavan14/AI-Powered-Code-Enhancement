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

class TestReverseString:
    def test_normal_string(self):
        assert reverse_string("hello") == "olleh"

    def test_empty_string(self):
        assert reverse_string("") == ""

    def test_palindrome(self):
        assert reverse_string("madam") == "madam"

    def test_string_with_spaces(self):
        assert reverse_string("hello world") == "dlrow olleh"

class TestWordCount:
    def test_normal_string(self):
        assert word_count("hello world") == 2

    def test_empty_string(self):
        assert word_count("") == 0

    def test_string_with_leading_and_trailing_spaces(self):
        assert word_count("  hello world  ") == 2

    def test_string_with_multiple_spaces(self):
        assert word_count("hello   world") == 2

    def test_string_with_tabs(self):
        assert word_count("hello\tworld") == 2

class TestToUpper:
    def test_normal_string(self):
        assert to_upper("hello") == "HELLO"

    def test_empty_string(self):
        assert to_upper("") == ""

    def test_string_with_mixed_case(self):
        assert to_upper("Hello World") == "HELLO WORLD"

    def test_string_with_numbers(self):
        assert to_upper("Hello 123") == "HELLO 123"

class TestIsEven:
    def test_even_number(self):
        assert is_even(2) == True

    def test_odd_number(self):
        assert is_even(3) == False

    def test_zero(self):
        assert is_even(0) == True

    def test_negative_even_number(self):
        assert is_even(-2) == True

    def test_negative_odd_number(self):
        assert is_even(-3) == False

class TestGenerateNumbers:
    def test_normal_range(self):
        assert generate_numbers(1, 5) == [1, 2, 3, 4, 5]

    def test_start_equals_end(self):
        assert generate_numbers(5, 5) == [5]

    def test_start_greater_than_end(self):
        assert generate_numbers(5, 1) == []

    def test_negative_range(self):
        assert generate_numbers(-3, 3) == [-3, -2, -1, 0, 1, 2, 3]

    def test_zero_range(self):
        assert generate_numbers(0, 0) == [0]