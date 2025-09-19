import json
from typing import Any, Dict, List, Optional


class PhabricatorAPIError(Exception):
    """Exception raised for Phabricator API errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        error_info: Optional[str] = None,
    ):
        self.error_code = error_code
        self.error_info = error_info
        super().__init__(message)


def process_api_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process API response and handle errors consistently.

    Args:
        response: Raw API response from Phabricator

    Returns:
        Processed response data

    Raises:
        PhabricatorAPIError: If the API response contains an error
    """
    if response.get("error_code"):
        raise PhabricatorAPIError(
            message=f"API Error: {response.get('error_info', 'Unknown error')}",
            error_code=response.get("error_code"),
            error_info=response.get("error_info"),
        )

    return response.get("result", {})


def validate_response_structure(
    response: Dict[str, Any], expected_keys: Optional[List[str]] = None
) -> bool:
    """
    Validate that the response has the expected structure.

    Args:
        response: API response to validate
        expected_keys: List of expected keys in the response

    Returns:
        True if response is valid, False otherwise
    """
    if not isinstance(response, dict):
        return False

    if expected_keys:
        return all(key in response for key in expected_keys)

    return True


def extract_data_from_response(response: Dict[str, Any], data_key: str = "data") -> Any:
    """
    Extract data from a standardized response structure.

    Args:
        response: API response
        data_key: Key where the data is stored

    Returns:
        The extracted data
    """
    if not validate_response_structure(response):
        raise ValueError("Invalid response structure")

    return response.get(data_key)


def safe_json_loads(json_str: str) -> Dict[str, Any]:
    """
    Safely load JSON string with error handling.

    Args:
        json_str: JSON string to parse

    Returns:
        Parsed JSON data

    Raises:
        ValueError: If JSON parsing fails
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response: {str(e)}")


def format_error_response(
    error: Exception, context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format a consistent error response.

    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred

    Returns:
        Formatted error response dictionary
    """
    error_info = {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
    }

    if context:
        error_info["context"] = context

    if isinstance(error, PhabricatorAPIError):
        error_info["error_code"] = error.error_code
        error_info["error_info"] = error.error_info

    return error_info
