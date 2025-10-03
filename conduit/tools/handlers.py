from functools import wraps
from typing import Any, Callable, Dict

from conduit.client import PhabricatorAPIError
from conduit.utils import ErrorCode


def _get_error_details(error: Exception) -> Dict[str, Any]:
    """
    Get simplified error information based on exception type.

    Args:
        error: The exception that occurred

    Returns:
        Dictionary containing error_code, error, and suggestion
    """
    error_code = ErrorCode.UNKNOWN_ERROR
    error_message = str(error)

    # Map exception types to error codes
    if isinstance(error, PhabricatorAPIError):
        if hasattr(error, "error_code") and error.error_code:
            try:
                error_code = ErrorCode(error.error_code)
            except ValueError:
                # Preserve unknown conduit error codes without failing the
                # error handler pipeline.
                error_code = ErrorCode.UNKNOWN_ERROR
    elif isinstance(error, (ConnectionError, TimeoutError)):
        error_code = ErrorCode.NETWORK_ERROR
    elif isinstance(error, (ValueError, KeyError)):
        error_code = ErrorCode.VALIDATION_ERROR

    # Provide generic suggestions based on error type
    suggestions = {
        ErrorCode.NETWORK_ERROR: "Check your network connection and verify the Phabricator server is accessible",
        ErrorCode.AUTH_ERROR: "Verify your PHABRICATOR_TOKEN environment variable or check token validity",
        ErrorCode.VALIDATION_ERROR: "Provide valid parameters according to the API documentation",
        ErrorCode.RATE_LIMIT_ERROR: "Wait a few minutes before making additional requests",
        ErrorCode.NOT_FOUND: "Verify the resource identifier and check if it exists",
    }

    suggestion = suggestions.get(
        error_code, "An unexpected error occurred. Please check the logs for details."
    )

    return {
        "error_code": error_code.value,
        "error": error_message,
        "suggestion": suggestion,
    }


def handle_api_errors(func: Callable) -> Callable:
    """
    Decorator to handle API errors and provide detailed error information.

    This decorator wraps API functions to catch exceptions and return
    structured error responses with error codes and suggestions.

    The decorator maintains backward compatibility by preserving the original
    error response structure while adding optional enhanced fields.

    Args:
        func: The function to decorate

    Returns:
        The wrapped function with error handling

    Example:
        @handle_api_errors
        def some_api_function():
            # API call logic here
            pass

        # Success response:
        # {"success": True, "result": {...}}

        # Error response:
        # {
        #     "success": False,
        #     "error": "Authentication failed: Invalid API token",
        #     "error_code": "AUTH_ERROR",
        #     "suggestion": "Verify your PHABRICATOR_TOKEN environment variable"
        # }
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        try:
            result = func(*args, **kwargs)
            # If the function returns a dict with 'success' key, return as-is
            # Otherwise, wrap the result in a success response
            if isinstance(result, dict) and "success" in result:
                return result
            return {"success": True, "result": result}
        except PhabricatorAPIError as e:
            error_details = _get_error_details(e)
            response = {
                "success": False,
                "error": error_details["error"],
                "error_code": error_details["error_code"],
                "suggestion": error_details["suggestion"],
            }
            # Maintain backward compatibility by keeping the original error message
            if hasattr(e, "error_info") and e.error_info:
                response["error_info"] = e.error_info
            return response
        except Exception as e:
            error_details = _get_error_details(e)
            response = {
                "success": False,
                "error": f"Parameter validation failed: {error_details['error']}",
                "error_code": error_details["error_code"],
                "suggestion": error_details["suggestion"],
            }
            # Maintain backward compatibility by keeping the original error message
            return response

    return wrapper
