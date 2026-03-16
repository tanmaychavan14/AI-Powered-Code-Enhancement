from datetime import datetime
import pytest

# Copy ALL function implementations at the top
class SomeClass:
    def format_join_date(self, date_string):
        """
        Format date into YYYY-MM-DD
        """
        # The strptime expects a string and raises ValueError for incorrect format
        # or invalid date values (e.g., 31-02-2023).
        # It raises TypeError if date_string is not a string.
        date_obj = datetime.strptime(date_string, "%d-%m-%Y")

        # BUG: wrong format - Corrected to YYYY-MM-DD as specified
        return date_obj.strftime("%Y-%m-%d")


# Pytest test cases
class TestSomeClass:
    @pytest.fixture
    def some_instance(self):
        """Fixture to provide an instance of SomeClass for tests."""
        return SomeClass()

    # Test normal operation with typical inputs
    def test_format_join_date_valid_common(self, some_instance):
        date_string = "15-01-2023"
        expected_format = "2023-01-15"
        assert some_instance.format_join_date(date_string) == expected_format

    # Test edge case: end of the year
    def test_format_join_date_valid_end_of_year(self, some_instance):
        date_string = "31-12-2024" # 2024 is a leap year
        expected_format = "2024-12-31"
        assert some_instance.format_join_date(date_string) == expected_format

    # Test edge case: leap year date
    def test_format_join_date_valid_leap_year_feb29(self, some_instance):
        date_string = "29-02-2024" # Valid date in a leap year
        expected_format = "2024-02-29"
        assert some_instance.format_join_date(date_string) == expected_format

    # Test error condition: invalid date (non-existent day for month)
    def test_format_join_date_invalid_date_non_existent(self, some_instance):
        date_string = "31-04-2023" # April only has 30 days
        with pytest.raises(ValueError, match="day is out of range for month"):
            some_instance.format_join_date(date_string)

    # Test error condition: invalid date (feb 29 on non-leap year)
    def test_format_join_date_invalid_date_non_leap_year_feb29(self, some_instance):
        date_string = "29-02-2023" # 2023 is not a leap year
        with pytest.raises(ValueError, match="day is out of range for month"):
            some_instance.format_join_date(date_string)

    # Test error condition: incorrect input format string
    def test_format_join_date_incorrect_input_format_string(self, some_instance):
        date_string = "2023-01-15" # Expected "DD-MM-YYYY" but got "YYYY-MM-DD"
        with pytest.raises(ValueError, match="time data '2023-01-15' does not match format '%d-%m-%Y'"):
            some_instance.format_join_date(date_string)

    # Test error condition: empty string input
    def test_format_join_date_empty_string_input(self, some_instance):
        date_string = ""
        with pytest.raises(ValueError, match="time data '' does not match format '%d-%m-%Y'"):
            some_instance.format_join_date(date_string)

    # Test error condition: None input (type check)
    def test_format_join_date_none_input(self, some_instance):
        date_string = None
        with pytest.raises(TypeError, match="strptime() argument 1 must be str, not NoneType"):
            some_instance.format_join_date(date_string)

    # Test error condition: non-string input (type check, e.g., integer)
    def test_format_join_date_non_string_input_int(self, some_instance):
        date_string = 15012023
        with pytest.raises(TypeError, match="strptime() argument 1 must be str, not int"):
            some_instance.format_join_date(date_string)