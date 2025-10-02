"""Tests for response utilities."""

import pytest

from src.utils.responses import (
    PhabricatorAPIError,
    extract_data_from_response,
    format_error_response,
    process_api_response,
    safe_json_loads,
    validate_response_structure,
)


class TestPhabricatorAPIError:
    """Test PhabricatorAPIError exception."""

    def test_phabricator_api_error_basic(self):
        """Test basic PhabricatorAPIError creation."""
        error = PhabricatorAPIError("Test error message")

        assert str(error) == "Test error message"
        assert error.error_code is None
        assert error.error_info is None

    def test_phabricator_api_error_with_code(self):
        """Test PhabricatorAPIError with error code."""
        error = PhabricatorAPIError(
            "Test error", error_code="ERR-123", error_info="Detailed error info"
        )

        assert str(error) == "Test error"
        assert error.error_code == "ERR-123"
        assert error.error_info == "Detailed error info"

    def test_phabricator_api_error_inheritance(self):
        """Test that PhabricatorAPIError inherits from Exception."""
        error = PhabricatorAPIError("Test")

        assert isinstance(error, Exception)
        assert isinstance(error, PhabricatorAPIError)


class TestProcessApiResponse:
    """Test API response processing."""

    def test_process_api_response_success(self):
        """Test processing successful API response."""
        response = {
            "result": {"data": [1, 2, 3]},
            "error_code": None,
            "error_info": None,
        }

        result = process_api_response(response)

        assert result == {"data": [1, 2, 3]}

    def test_process_api_response_with_error(self):
        """Test processing API response with error."""
        response = {
            "result": None,
            "error_code": "ERR-INVALID",
            "error_info": "Invalid request parameters",
        }

        with pytest.raises(PhabricatorAPIError) as exc_info:
            process_api_response(response)

        assert "API Error: Invalid request parameters" in str(exc_info.value)
        assert exc_info.value.error_code == "ERR-INVALID"
        assert exc_info.value.error_info == "Invalid request parameters"

    def test_process_api_response_missing_result(self):
        """Test processing response without result field."""
        response = {
            "error_code": None,
            "error_info": None,
        }

        result = process_api_response(response)

        assert result == {}

    def test_process_api_response_empty_result(self):
        """Test processing response with empty result."""
        response = {
            "result": {},
            "error_code": None,
            "error_info": None,
        }

        result = process_api_response(response)

        assert result == {}


class TestValidateResponseStructure:
    """Test response structure validation."""

    def test_validate_response_structure_valid_dict(self):
        """Test validating valid dictionary response."""
        response = {"data": [1, 2, 3], "count": 3}

        assert validate_response_structure(response) is True

    def test_validate_response_structure_invalid_type(self):
        """Test validating non-dictionary response."""
        response = "not a dict"

        assert validate_response_structure(response) is False

    def test_validate_response_structure_with_expected_keys_present(self):
        """Test validating response with all expected keys present."""
        response = {"data": [1, 2, 3], "cursor": "token123"}
        expected_keys = ["data", "cursor"]

        assert validate_response_structure(response, expected_keys) is True

    def test_validate_response_structure_with_expected_keys_missing(self):
        """Test validating response with missing expected keys."""
        response = {"data": [1, 2, 3]}
        expected_keys = ["data", "cursor"]

        assert validate_response_structure(response, expected_keys) is False

    def test_validate_response_structure_empty_expected_keys(self):
        """Test validating response with empty expected keys list."""
        response = {"data": [1, 2, 3]}
        expected_keys = []

        assert validate_response_structure(response, expected_keys) is True

    def test_validate_response_structure_none_expected_keys(self):
        """Test validating response with None expected keys."""
        response = {"data": [1, 2, 3]}

        assert validate_response_structure(response, None) is True


class TestExtractDataFromResponse:
    """Test data extraction from responses."""

    def test_extract_data_from_response_valid(self):
        """Test extracting data from valid response."""
        response = {"data": [1, 2, 3], "count": 3}

        result = extract_data_from_response(response)

        assert result == [1, 2, 3]

    def test_extract_data_from_response_custom_key(self):
        """Test extracting data from custom key."""
        response = {"results": [1, 2, 3], "count": 3}

        result = extract_data_from_response(response, data_key="results")

        assert result == [1, 2, 3]

    def test_extract_data_from_response_missing_key(self):
        """Test extracting data when key is missing."""
        response = {"count": 3}

        result = extract_data_from_response(response)

        assert result is None

    def test_extract_data_from_response_invalid_structure(self):
        """Test extracting data from invalid response structure."""
        response = "not a dict"

        with pytest.raises(ValueError) as exc_info:
            extract_data_from_response(response)

        assert "Invalid response structure" in str(exc_info.value)


class TestSafeJsonLoads:
    """Test safe JSON loading."""

    def test_safe_json_loads_valid(self):
        """Test loading valid JSON string."""
        json_str = '{"data": [1, 2, 3], "count": 3}'

        result = safe_json_loads(json_str)

        assert result == {"data": [1, 2, 3], "count": 3}

    def test_safe_json_loads_invalid(self):
        """Test loading invalid JSON string."""
        json_str = '{"invalid": json}'

        with pytest.raises(ValueError) as exc_info:
            safe_json_loads(json_str)

        assert "Invalid JSON response" in str(exc_info.value)

    def test_safe_json_loads_empty_string(self):
        """Test loading empty JSON string."""
        json_str = ""

        with pytest.raises(ValueError) as exc_info:
            safe_json_loads(json_str)

        assert "Invalid JSON response" in str(exc_info.value)

    def test_safe_json_loads_malformed(self):
        """Test loading malformed JSON string."""
        json_str = '{"unclosed": "object"'

        with pytest.raises(ValueError) as exc_info:
            safe_json_loads(json_str)

        assert "Invalid JSON response" in str(exc_info.value)


class TestFormatErrorResponse:
    """Test error response formatting."""

    def test_format_error_response_basic(self):
        """Test formatting basic error response."""
        error = Exception("Test error")

        result = format_error_response(error)

        assert result["success"] is False
        assert result["error"] == "Test error"
        assert result["error_type"] == "Exception"
        assert "context" not in result

    def test_format_error_response_with_context(self):
        """Test formatting error response with context."""
        error = ValueError("Invalid value")
        context = "user_search"

        result = format_error_response(error, context)

        assert result["success"] is False
        assert result["error"] == "Invalid value"
        assert result["error_type"] == "ValueError"
        assert result["context"] == "user_search"

    def test_format_error_response_phabricator_error(self):
        """Test formatting PhabricatorAPIError response."""
        error = PhabricatorAPIError(
            "API error", error_code="ERR-123", error_info="Detailed info"
        )

        result = format_error_response(error)

        assert result["success"] is False
        assert result["error"] == "API error"
        assert result["error_type"] == "PhabricatorAPIError"
        assert result["error_code"] == "ERR-123"
        assert result["error_info"] == "Detailed info"

    def test_format_error_response_phabricator_error_with_context(self):
        """Test formatting PhabricatorAPIError with context."""
        error = PhabricatorAPIError(
            "API error", error_code="ERR-123", error_info="Detailed info"
        )
        context = "task_creation"

        result = format_error_response(error, context)

        assert result["success"] is False
        assert result["error"] == "API error"
        assert result["error_type"] == "PhabricatorAPIError"
        assert result["error_code"] == "ERR-123"
        assert result["error_info"] == "Detailed info"
        assert result["context"] == "task_creation"

    def test_format_error_response_custom_exception(self):
        """Test formatting custom exception."""

        class CustomError(Exception):
            pass

        error = CustomError("Custom message")

        result = format_error_response(error)

        assert result["success"] is False
        assert result["error"] == "Custom message"
        assert result["error_type"] == "CustomError"
