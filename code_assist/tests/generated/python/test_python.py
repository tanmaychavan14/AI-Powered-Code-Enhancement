import pytest

# Copy of the original Python functions for testing
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

# --- Pytest Test Cases ---

class TestReverseString:
    def test_reverse_string_normal_case(self):
        assert reverse_string("hello") == "olleh"

    def test_reverse_string_with_spaces(self):
        assert reverse_string("Hello World") == "dlroW olleH"

    def test_reverse_string_empty_string(self):
        assert reverse_string("") == ""

    def test_reverse_string_single_character(self):
        assert reverse_string("a") == "a"

    def test_reverse_string_numbers_and_symbols(self):
        assert reverse_string("123!@#") == "#@!321"

    def test_reverse_string_unicode(self):
        assert reverse_string("été") == "été" # Should reverse correctly

    def test_reverse_string_non_string_input_type_error(self):
        with pytest.raises(TypeError):
            reverse_string(123)
        with pytest.raises(TypeError):
            reverse_string(None)
        with pytest.raises(TypeError):
            reverse_string(['a', 'b']) # Slicing works, but it's not a string


class TestWordCount:
    def test_word_count_normal_two_words(self):
        assert word_count("Hello world") == 2

    def test_word_count_multiple_words(self):
        assert word_count("This is a test sentence") == 5

    def test_word_count_single_word(self):
        assert word_count("Python") == 1

    def test_word_count_empty_string(self):
        assert word_count("") == 0

    def test_word_count_leading_trailing_spaces(self):
        assert word_count("  leading and trailing  ") == 4

    def test_word_count_multiple_internal_spaces(self):
        assert word_count("one   two    three") == 3

    def test_word_count_non_string_input_attribute_error(self):
        with pytest.raises(AttributeError):
            word_count(123)
        with pytest.raises(AttributeError):
            word_count(None)


class TestToUpper:
    def test_to_upper_lowercase(self):
        assert to_upper("hello") == "HELLO"

    def test_to_upper_mixed_case(self):
        assert to_upper("Hello World") == "HELLO WORLD"

    def test_to_upper_already_uppercase(self):
        assert to_upper("PYTHON") == "PYTHON"

    def test_to_upper_empty_string(self):
        assert to_upper("") == ""

    def test_to_upper_with_numbers_symbols(self):
        assert to_upper("123!@abc") == "123!@ABC"

    def test_to_upper_non_string_input_attribute_error(self):
        with pytest.raises(AttributeError):
            to_upper(123)
        with pytest.raises(AttributeError):
            to_upper(None)


class TestIsEven:
    def test_is_even_positive_even(self):
        assert is_even(4) is True

    def test_is_even_positive_odd(self):
        assert is_even(7) is False

    def test_is_even_zero(self):
        assert is_even(0) is True

    def test_is_even_negative_even(self):
        assert is_even(-2) is True

    def test_is_even_negative_odd(self):
        assert is_even(-3) is False

    def test_is_even_large_number(self):
        assert is_even(1000000) is True
        assert is_even(999999) is False

    def test_is_even_non_integer_type_error(self):
        with pytest.raises(TypeError):
            is_even(3.5) # Modulo operator also works on floats
        with pytest.raises(TypeError):
            is_even("hello")
        with pytest.raises(TypeError):
            is_even(None)


class TestGenerateNumbers:
    def test_generate_numbers_positive_range(self):
        assert generate_numbers(1, 5) == [1, 2, 3, 4, 5]

    def test_generate_numbers_single_number(self):
        assert generate_numbers(7, 7) == [7]

    def test_generate_numbers_zero_to_positive(self):
        assert generate_numbers(0, 3) == [0, 1, 2, 3]

    def test_generate_numbers_negative_range(self):
        assert generate_numbers(-3, -1) == [-3, -2, -1]

    def test_generate_numbers_across_zero(self):
        assert generate_numbers(-1, 1) == [-1, 0, 1]

    def test_generate_numbers_empty_range_start_greater_than_end(self):
        assert generate_numbers(5, 3) == []

    def test_generate_numbers_large_range(self):
        expected = list(range(1, 101))
        assert generate_numbers(1, 100) == expected

    def test_generate_numbers_non_integer_start_type_error(self):
        with pytest.raises(TypeError):
            generate_numbers("1", 5)
        with pytest.raises(TypeError):
            generate_numbers(1.5, 5)

    def test_generate_numbers_non_integer_end_type_error(self):
        with pytest.raises(TypeError):
            generate_numbers(1, None)
        with pytest.raises(TypeError):
            generate_numbers(1, "5")