import pytest

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


class TestStringOperations:

    @pytest.mark.parametrize("input_text, expected_output", [
        ("hello", "olleh"),
        ("Python", "nohtyP"),
        ("a", "a"),
        ("", ""),
        ("racecar", "racecar"),
        ("123 abc!", "!cba 321"),
    ])
    def test_reverse_string_normal_and_edge_cases(self, input_text, expected_output):
        """Test reverse_string with typical, empty, and special character inputs."""
        assert reverse_string(input_text) == expected_output
        assert isinstance(reverse_string(input_text), str)

    @pytest.mark.parametrize("invalid_input", [
        123,
        None,
        ["a", "b", "c"],  # List slicing works, but type is list. Still good to check
        (1, 2, 3), # Tuple slicing works, but type is tuple. Still good to check
    ])
    def test_reverse_string_invalid_input_type(self, invalid_input):
        """Test reverse_string with invalid input types."""
        # Note: text[::-1] actually works for lists and tuples, returning a list or tuple.
        # So we check for non-string types where the *expected* return type is string.
        if not isinstance(invalid_input, (str, list, tuple)):
            with pytest.raises(TypeError):
                reverse_string(invalid_input)
        else:
            # For lists and tuples, slicing works, but the return type won't be str
            assert type(reverse_string(invalid_input)) == type(invalid_input)


    @pytest.mark.parametrize("input_text, expected_count", [
        ("hello world", 2),
        ("one", 1),
        ("  multiple   spaces  between words ", 4),
        (" leading and trailing spaces ", 4),
        ("", 0),
        ("   ", 0),  # Only spaces
        ("pytest_framework", 1), # Single word with underscore
        ("1 2 3 4", 4),
    ])
    def test_word_count_normal_and_edge_cases(self, input_text, expected_count):
        """Test word_count with various string inputs including spaces and empty."""
        assert word_count(input_text) == expected_count
        assert isinstance(word_count(input_text), int)

    @pytest.mark.parametrize("invalid_input", [
        123,
        None,
        ["a", "b"],
        {"key": "value"},
    ])
    def test_word_count_invalid_input_type(self, invalid_input):
        """Test word_count with non-string input types."""
        with pytest.raises(AttributeError):
            word_count(invalid_input)


    @pytest.mark.parametrize("input_text, expected_output", [
        ("hello world", "HELLO WORLD"),
        ("PYTHON", "PYTHON"),
        ("PyTest", "PYTEST"),
        ("123 abc!", "123 ABC!"),
        ("", ""),
        ("   ", "   "),
    ])
    def test_to_upper_normal_and_edge_cases(self, input_text, expected_output):
        """Test to_upper with various string inputs including empty and already uppercase."""
        assert to_upper(input_text) == expected_output
        assert isinstance(to_upper(input_text), str)

    @pytest.mark.parametrize("invalid_input", [
        123,
        None,
        ["a", "b"],
        {"key": "value"},
    ])
    def test_to_upper_invalid_input_type(self, invalid_input):
        """Test to_upper with non-string input types."""
        with pytest.raises(AttributeError):
            to_upper(invalid_input)


class TestNumberOperations:

    @pytest.mark.parametrize("input_num, expected_result", [
        (4, True),
        (0, True),
        (-2, True),
        (100, True),
        (7, False),
        (1, False),
        (-5, False),
        (99, False),
    ])
    def test_is_even_integer_inputs(self, input_num, expected_result):
        """Test is_even with various integer inputs (positive, negative, zero)."""
        assert is_even(input_num) == expected_result
        assert isinstance(is_even(input_num), bool)

    @pytest.mark.parametrize("input_num, expected_result", [
        (4.0, True),  # 4.0 % 2 == 0.0
        (0.0, True),
        (-2.0, True),
        (7.0, False),  # 7.0 % 2 == 1.0
        (3.5, False),  # 3.5 % 2 == 1.5
        (-1.5, False), # -1.5 % 2 == 0.5
    ])
    def test_is_even_float_inputs(self, input_num, expected_result):
        """Test is_even with float inputs, considering modulo behavior."""
        assert is_even(input_num) == expected_result
        assert isinstance(is_even(input_num), bool)

    @pytest.mark.parametrize("invalid_input", [
        "abc",
        None,
        [],
        {"key": 1},
    ])
    def test_is_even_invalid_input_type(self, invalid_input):
        """Test is_even with non-numeric input types."""
        with pytest.raises(TypeError):
            is_even(invalid_input)


    @pytest.mark.parametrize("start, end, expected_list", [
        (1, 5, [1, 2, 3, 4, 5]),
        (0, 0, [0]),
        (5, 5, [5]),
        (-3, 1, [-3, -2, -1, 0, 1]),
        (10, 7, []),  # Start > End
        (-5, -2, [-5, -4, -3, -2]),
        (0, 5, [0, 1, 2, 3, 4, 5]),
    ])
    def test_generate_numbers_normal_and_edge_cases(self, start, end, expected_list):
        """Test generate_numbers with various start/end combinations including empty range."""
        result = generate_numbers(start, end)
        assert result == expected_list
        assert isinstance(result, list)
        for num in result:
            assert isinstance(num, int)

    @pytest.mark.parametrize("start, end", [
        ("a", 5),
        (1, "b"),
        (None, 10),
        (5, None),
        ([], 1),
        (1, {}),
    ])
    def test_generate_numbers_invalid_input_type(self, start, end):
        """Test generate_numbers with non-integer input types for start or end."""
        with pytest.raises(TypeError):
            generate_numbers(start, end)