from functools import wraps
from typing import Any, Callable, Dict

from src.tools.pagination import _apply_smart_pagination, _truncate_text_response


def optimize_token_usage(func: Callable) -> Callable:
    """
    Decorator to optimize token usage by applying smart limits and truncation.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # Apply token optimization to search results
        if isinstance(result, dict) and "data" in result:
            # Check if this is a search result that needs optimization
            data = result["data"]
            if isinstance(data, list) and len(data) > 50:
                # Apply smart pagination
                optimized_result = _apply_smart_pagination(
                    data, kwargs.get("limit", 100)
                )
                result.update(optimized_result)

        return result

    return wrapper


def optimize_search_results(
    result: Dict[str, Any], max_tokens: int = 5000
) -> Dict[str, Any]:
    """
    Apply token optimization to search results based on max_tokens budget.

    Args:
        result: Original search result
        max_tokens: Maximum token budget for response

    Returns:
        Optimized result with token budget applied
    """
    if not max_tokens or not result.get("data"):
        return result

    data = result["data"]
    if isinstance(data, list):
        # Calculate optimal limit based on token budget
        # This is a heuristic - adjust based on actual token usage patterns
        if len(data) > 20:  # Apply optimization for large results
            optimized_data = data[:20]
            result["data"] = optimized_data
            result["token_optimization"] = {
                "applied": True,
                "original_count": len(data),
                "returned_count": 20,
                "reason": "Token budget optimization",
                "max_tokens": max_tokens,
            }

    return result


def optimize_large_text(text: str, max_length: int = 2000) -> Dict[str, Any]:
    """
    Optimize large text responses by truncating them.

    Args:
        text: The text to optimize
        max_length: Maximum allowed length

    Returns:
        Optimized text response
    """
    return _truncate_text_response(text, max_length)
