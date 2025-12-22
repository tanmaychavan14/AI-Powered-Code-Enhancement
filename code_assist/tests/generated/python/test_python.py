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


# Test cases for reverse_string(text)
@pytest.mark.parametrize("input_text, expected_output", [
    ("hello", "olleh"),
    ("world", "dlrow"),
    ("Python", "nohtyP"),
    ("A man, a plan, a canal: Panama", "amanaP :lanac a ,nalp a ,nam A"),
    ("", ""), # Edge case: empty string
    ("a", "a"), # Edge case: single character
    (" ", " "), # Edge case: single space
    ("12345", "54321"), # Numbers as string
    ("!@#$", "$#@!"), # Special characters
])
def test_reverse_string_valid_inputs(input_text, expected_output):
    """Test reverse_string with various valid string inputs."""
    assert reverse_string(input_text) == expected_output
    assert isinstance(reverse_string(input_text), str)

def test_reverse_string_type_error_for_non_string():
    """Test reverse_string raises TypeError for non-string input."""
    with pytest.raises(TypeError):
        reverse_string(123)
    with pytest.raises(TypeError):
        reverse_string(['a', 'b'])

# Test cases for word_count(text)
@pytest.mark.parametrize("input_text, expected_count", [
    ("hello world", 2),
    ("This is a test sentence.", 5),
    ("singleword", 1),
    ("", 0), # Edge case: empty string
    ("   ", 0), # Edge case: only spaces
    ("  leading and trailing spaces ", 4), # Edge case: leading/trailing spaces
    ("words   with   multiple  spaces", 4), # Edge case: multiple spaces between words
    ("123 456 test", 3), # Numbers in words
    ("word-with-hyphen hyphenated-word", 2), # Hyphenated words are treated as one by split()
])
def test_word_count_valid_inputs(input_text, expected_count):
    """Test word_count with various valid string inputs."""
    assert word_count(input_text) == expected_count
    assert isinstance(word_count(input_text), int)

def test_word_count_type_error_for_non_string():
    """Test word_count raises AttributeError for non-string input."""
    with pytest.raises(AttributeError):
        word_count(123)
    with pytest.raises(AttributeError):
        word_count(['a', 'b'])

# Test cases for to_upper(text)
@pytest.mark.parametrize("input_text, expected_output", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("PYTHON", "PYTHON"), # Already uppercase
    ("mixed Case String", "MIXED CASE STRING"),
    ("123", "123"), # Numbers should remain unchanged
    ("!@#$", "!@#$"), # Special characters should remain unchanged
    ("", ""), # Edge case: empty string
    ("a", "A"), # Edge case: single character
])
def test_to_upper_valid_inputs(input_text, expected_output):
    """Test to_upper with various valid string inputs."""
    assert to_upper(input_text) == expected_output
    assert isinstance(to_upper(input_text), str)

def test_to_upper_type_error_for_non_string():
    """Test to_upper raises AttributeError for non-string input."""
    with pytest.raises(AttributeError):
        to_upper(123)
    with pytest.raises(AttributeError):
        to_upper(['a', 'b'])

# Test cases for is_even(num)
@pytest.mark.parametrize("input_num, expected_bool", [
    (2, True),
    (4, True),
    (0, True), # Edge case: zero
    (100, True),
    (-2, True), # Negative even
    (1, False),
    (3, False),
    (99, False),
    (-1, False), # Negative odd
    (2**30, True), # Large even number
    (2**30 + 1, False), # Large odd number
])
def test_is_even_valid_inputs(input_num, expected_bool):
    """Test is_even with various valid integer inputs."""
    assert is_even(input_num) == expected_bool
    assert isinstance(is_even(input_num), bool)

def test_is_even_type_error_for_non_integer():
    """Test is_even raises TypeError for non-integer input."""
    with pytest.raises(TypeError):
        is_even(1.5) # Float
    with pytest.raises(TypeError):
        is_even("two") # String
    with pytest.raises(TypeError):
        is_even([2]) # List
    with pytest.raises(TypeError):
        is_even(None) # None type

# Test cases for generate_numbers(start, end)
@pytest.mark.parametrize("start, end, expected_list", [
    (1, 5, [1, 2, 3, 4, 5]),
    (0, 0, [0]), # Edge case: start == end
    (5, 5, [5]), # Another start == end
    (-2, 2, [-2, -1, 0, 1, 2]),
    (10, 7, []), # Edge case: start > end (empty list)
    (0, 3, [0, 1, 2, 3]),
    (-5, -3, [-5, -4, -3]),
    (1, 100, list(range(1, 101))), # Larger range
])
def test_generate_numbers_valid_inputs(start, end, expected_list):
    """Test generate_numbers with various valid integer start and end values."""
    assert generate_numbers(start, end) == expected_list
    assert isinstance(generate_numbers(start, end), list)
    if expected_list: # Check type of elements if list is not empty
        assert all(isinstance(x, int) for x in generate_numbers(start, end))

def test_generate_numbers_type_error_for_non_integer_inputs():
    """Test generate_numbers raises TypeError for non-integer start or end."""
    with pytest.raises(TypeError):
        generate_numbers(1.0, 5)
    with pytest.raises(TypeError):
        generate_numbers(1, 5.0)
    with pytest.raises(TypeError):
        generate_numbers("1", 5)
    with pytest.raises(TypeError):
        generate_numbers(1, "5")
    with pytest.raises(TypeError):
        generate_numbers(None, 5)