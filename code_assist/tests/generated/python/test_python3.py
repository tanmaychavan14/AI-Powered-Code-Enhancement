# data_service.py

import requests
import json
from datetime import datetime
from statistics import mean


class DataService:

    def fetch_user(self, user_id):
        """
        Fetch user data from API
        """
        url = f"https://jsonplaceholder.typicode.com/users/{user_id}"
        response = requests.get(url)

        # BUG: missing status code check
        return response.json()


    def get_user_email(self, user_data):
        """
        Extract user email
        """
        # BUG: wrong key
        return user_data["mail"]


    def calculate_average_age(self, users):
        """
        Calculate average age
        """
        ages = [user["age"] for user in users]

        # BUG: incorrect logic
        return sum(ages)


    def parse_json_data(self, json_string):
        """
        Parse JSON string
        """
        data = json.loads(json_string)

        # BUG: should validate structure
        return data["data"]


    def format_join_date(self, date_string):
        """
        Format date into YYYY-MM-DD
        """
        date_obj = datetime.strptime(date_string, "%d-%m-%Y")

        # BUG: wrong format
        return date_obj.strftime("%Y/%m/%d")

# --- End of copied Python code ---

import pytest
import requests
import json
from datetime import datetime
from unittest.mock import Mock, patch


@pytest.fixture
def data_service():
    """Provides a DataService instance for tests."""
    return DataService()


# Test cases for fetch_user(self, user_id)
def test_fetch_user_success(data_service, mocker):
    """
    Tests successful fetching of a user.
    Mocks requests.get to return a valid user response.
    """
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    expected_user_data = {"id": 1, "name": "Leanne Graham", "username": "Bret", "email": "Sincere@april.biz"}
    mock_response.json.return_value = expected_user_data
    mocker.patch('requests.get', return_value=mock_response)

    user = data_service.fetch_user(1)
    assert user == expected_user_data
    requests.get.assert_called_once_with("https://jsonplaceholder.typicode.com/users/1")


def test_fetch_user_not_found_returns_empty_json(data_service, mocker):
    """
    Tests fetching a non-existent user where the API returns a 404-like response
    but with a valid (e.g., empty) JSON body. The current buggy implementation
    returns whatever `response.json()` provides.
    """
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    expected_error_data = {}  # A common API response for "not found"
    mock_response.json.return_value = expected_error_data
    mocker.patch('requests.get', return_value=mock_response)

    user = data_service.fetch_user(999)  # Non-existent user ID
    assert user == expected_error_data
    requests.get.assert_called_once_with("https://jsonplaceholder.typicode.com/users/999")


def test_fetch_user_api_error_invalid_json_response(data_service, mocker):
    """
    Tests an API error (e.g., 500) where the response body is not valid JSON.
    The buggy implementation will attempt `response.json()` and raise `json.decoder.JSONDecodeError`.
    """
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    mock_response.json.side_effect = json.decoder.JSONDecodeError("Expecting value", "<html>Error</html>", 0)
    mocker.patch('requests.get', return_value=mock_response)

    with pytest.raises(json.decoder.JSONDecodeError):
        data_service.fetch_user(1)
    requests.get.assert_called_once_with("https://jsonplaceholder.typicode.com/users/1")


def test_fetch_user_network_error(data_service, mocker):
    """
    Tests a network connection error by mocking `requests.get` to raise `ConnectionError`.
    """
    mocker.patch('requests.get', side_effect=requests.exceptions.ConnectionError("Network is down"))

    with pytest.raises(requests.exceptions.ConnectionError):
        data_service.fetch_user(1)
    requests.get.assert_called_once_with("https://jsonplaceholder.typicode.com/users/1")


def test_fetch_user_with_string_user_id(data_service, mocker):
    """
    Tests fetch_user with a user_id of a string type. The URL will be formed with the string,
    and the mocked response is returned.
    """
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    expected_user_data = {"id": "test_id", "name": "Test User"}
    mock_response.json.return_value = expected_user_data
    mocker.patch('requests.get', return_value=mock_response)

    user_id_str = "test_id"
    user = data_service.fetch_user(user_id_str)
    assert user == expected_user_data
    requests.get.assert_called_once_with(f"https://jsonplaceholder.typicode.com/users/{user_id_str}")


# Test cases for get_user_email(self, user_data)
def test_get_user_email_success_with_buggy_key(data_service):
    """
    Tests successful extraction when the 'mail' key is present,
    reflecting the buggy behavior.
    """
    user_data = {"id": 1, "name": "Test User", "mail": "test@example.com", "email": "correct@example.com"}
    email = data_service.get_user_email(user_data)
    assert email == "test@example.com"


def test_get_user_email_raises_keyerror_for_correct_email_key(data_service):
    """
    Tests extraction when only the 'email' key (the standard one) is present,
    but 'mail' is missing, leading to a KeyError due to the bug.
    """
    user_data = {"id": 1, "name": "Test User", "email": "correct@example.com"}
    with pytest.raises(KeyError, match="'mail'"):
        data_service.get_user_email(user_data)


def test_get_user_email_raises_keyerror_for_missing_key(data_service):
    """
    Tests extraction when neither 'mail' nor 'email' key is present.
    """
    user_data = {"id": 1, "name": "Test User"}
    with pytest.raises(KeyError, match="'mail'"):
        data_service.get_user_email(user_data)


def test_get_user_email_empty_user_data(data_service):
    """
    Tests with an empty dictionary as user data, expecting KeyError.
    """
    user_data = {}
    with pytest.raises(KeyError, match="'mail'"):
        data_service.get_user_email(user_data)


def test_get_user_email_none_user_data_raises_typeerror(data_service):
    """
    Tests with None as user_data, expecting a TypeError.
    """
    user_data = None
    with pytest.raises(TypeError):
        data_service.get_user_email(user_data)


def test_get_user_email_non_dict_user_data_raises_typeerror(data_service):
    """
    Tests with a non-dictionary input for user_data, expecting a TypeError.
    """
    user_data = "not a dict"
    with pytest.raises(TypeError):
        data_service.get_user_email(user_data)


# Test cases for calculate_average_age(self, users)
def test_calculate_average_age_multiple_users_returns_sum(data_service):
    """
    Tests calculation with multiple users, verifying it returns the sum of ages,
    not the average, due to the bug.
    """
    users = [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
        {"name": "Charlie", "age": 35},
    ]
    # BUG: The code returns sum, not average.
    expected_sum = 25 + 30 + 35
    result = data_service.calculate_average_age(users)
    assert result == expected_sum


def test_calculate_average_age_single_user_returns_age(data_service):
    """
    Tests calculation with a single user, verifying it returns the age.
    """
    users = [{"name": "David", "age": 40}]
    expected_sum = 40
    result = data_service.calculate_average_age(users)
    assert result == expected_sum


def test_calculate_average_age_empty_list_returns_zero(data_service):
    """
    Tests calculation with an empty list of users. `sum([])` returns 0.
    """
    users = []
    result = data_service.calculate_average_age(users)
    assert result == 0


def test_calculate_average_age_users_with_zero_age(data_service):
    """
    Tests calculation with users having zero age, verifying the correct sum.
    """
    users = [
        {"name": "Eve", "age": 0},
        {"name": "Frank", "age": 10},
    ]
    expected_sum = 0 + 10
    result = data_service.calculate_average_age(users)
    assert result == expected_sum


def test_calculate_average_age_missing_age_key_raises_keyerror(data_service):
    """
    Tests calculation when a user is missing the 'age' key, expecting KeyError.
    """
    users = [
        {"name": "Grace", "age": 28},
        {"name": "Heidi"},  # Missing 'age'
    ]
    with pytest.raises(KeyError, match="'age'"):
        data_service.calculate_average_age(users)


def test_calculate_average_age_non_numeric_age_raises_typeerror(data_service):
    """
    Tests calculation when a user has a non-numeric age, expecting TypeError during sum.
    """
    users = [
        {"name": "Ivan", "age": 22},
        {"name": "Judy", "age": "thirty"},  # Non-numeric age
    ]
    with pytest.raises(TypeError):
        data_service.calculate_average_age(users)


# Test cases for parse_json_data(self, json_string)
def test_parse_json_data_success_with_data_key(data_service):
    """
    Tests successful parsing when the 'data' key is present in the JSON.
    """
    json_string = '{"status": "success", "data": [{"id": 1, "value": "test"}]}'
    expected_data = [{"id": 1, "value": "test"}]
    result = data_service.parse_json_data(json_string)
    assert result == expected_data


def test_parse_json_data_without_data_key_raises_keyerror(data_service):
    """
    Tests parsing JSON without the required 'data' key, expecting KeyError due to the bug.
    """
    json_string = '{"status": "error", "message": "no data"}'
    with pytest.raises(KeyError, match="'data'"):
        data_service.parse_json_data(json_string)


def test_parse_json_data_empty_json_object_raises_keyerror(data_service):
    """
    Tests parsing an empty JSON object, expecting KeyError for 'data'.
    """
    json_string = '{}'
    with pytest.raises(KeyError, match="'data'"):
        data_service.parse_json_data(json_string)


def test_parse_json_data_malformed_json_raises_jsondecodeerror(data_service):
    """
    Tests parsing a malformed JSON string, expecting `json.decoder.JSONDecodeError`.
    """
    json_string = '{"data": "invalid json'  # Missing closing quote and brace
    with pytest.raises(json.decoder.JSONDecodeError):
        data_service.parse_json_data(json_string)


def test_parse_json_data_empty_string_raises_jsondecodeerror(data_service):
    """
    Tests parsing an empty string, expecting `json.decoder.JSONDecodeError`.
    """
    json_string = ''
    with pytest.raises(json.decoder.JSONDecodeError):
        data_service.parse_json_data(json_string)


def test_parse_json_data_data_key_with_empty_value(data_service):
    """
    Tests parsing JSON where 'data' key is present but its value is an empty list or dictionary.
    """
    json_string_list = '{"data": []}'
    assert data_service.parse_json_data(json_string_list) == []

    json_string_dict = '{"data": {}}'
    assert data_service.parse_json_data(json_string_dict) == {}


# Test cases for format_join_date(self, date_string)
def test_format_join_date_success_buggy_format(data_service):
    """
    Tests successful formatting with a valid date string.
    Verifies the buggy output format YYYY/MM/DD.
    """
    date_string = "15-08-2023"
    expected_formatted_date = "2023/08/15"  # BUG: Should be 2023-08-15
    result = data_service.format_join_date(date_string)
    assert result == expected_formatted_date


def test_format_join_date_with_single_digit_day_month(data_service):
    """
    Tests formatting with single-digit day and month inputs.
    """
    date_string = "01-01-2024"
    expected_formatted_date = "2024/01/01"
    result = data_service.format_join_date(date_string)
    assert result == expected_formatted_date


def test_format_join_date_leap_year(data_service):
    """
    Tests formatting a date within a leap year.
    """
    date_string = "29-02-2024"
    expected_formatted_date = "2024/02/29"
    result = data_service.format_join_date(date_string)
    assert result == expected_formatted_date


def test_format_join_date_invalid_input_format_raises_valueerror(data_service):
    """
    Tests formatting with an invalid date string format (e.g., MM/DD/YYYY instead of DD-MM-YYYY),
    expecting ValueError from `strptime`.
    """
    date_string = "2023/08/15"  # Expected "DD-MM-YYYY"
    with pytest.raises(ValueError, match="time data '2023/08/15' does not match format '%d-%m-%Y'"):
        data_service.format_join_date(date_string)


def test_format_join_date_invalid_date_value_raises_valueerror(data_service):
    """
    Tests formatting with an invalid date value (e.g., 32nd day of a month),
    expecting ValueError from `strptime`.
    """
    date_string = "32-01-2023"
    with pytest.raises(ValueError, match="day is out of range for month"):
        data_service.format_join_date(date_string)


def test_format_join_date_empty_string_raises_valueerror(data_service):
    """
    Tests formatting an empty string, expecting ValueError from `strptime`.
    """
    date_string = ""
    with pytest.raises(ValueError, match="time data '' does not match format '%d-%m-%Y'"):
        data_service.format_join_date(date_string)


def test_format_join_date_none_input_raises_typeerror(data_service):
    """
    Tests formatting with None input, expecting TypeError.
    """
    date_string = None
    with pytest.raises(TypeError):
        data_service.format_join_date(date_string)