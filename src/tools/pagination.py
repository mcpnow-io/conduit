from typing import Any


def _add_pagination_metadata(result: dict, cursor: dict = None) -> dict:
    """
    Add pagination metadata to search results.

    Args:
        result: Original search result
        cursor: Pagination cursor from API

    Returns:
        Result with enhanced pagination metadata
    """
    if cursor:
        result["pagination"] = {
            "cursor": cursor,
            "has_more": cursor.get("after") is not None,
            "limit": cursor.get("limit", 100),
        }

    return result


def _apply_smart_pagination(data: list[Any], limit: int = None) -> dict:
    """
    Apply smart pagination to data with token optimization.

    Args:
        data: List of data items
        limit: Maximum number of items to return (optional)

    Returns:
        Paginated response with metadata
    """
    if limit is None:
        limit = 100  # Default limit

    # Apply limit if data is larger than limit
    if len(data) > limit:
        paginated_data = data[:limit]
        has_more = True
        total_count = len(data)
        suggestion = f"Use pagination to retrieve remaining {total_count - limit} items"
    else:
        paginated_data = data
        has_more = False
        total_count = len(data)
        suggestion = None

    return {
        "data": paginated_data,
        "pagination": {
            "total": total_count,
            "returned": len(paginated_data),
            "has_more": has_more,
        },
        "suggestion": suggestion,
    }


def _truncate_text_response(text: str, max_length: int = 2000) -> dict:
    """
    Truncate long text responses with helpful guidance.

    Args:
        text: The text to truncate
        max_length: Maximum allowed length

    Returns:
        Truncated response with guidance
    """
    if len(text) <= max_length:
        return {"content": text, "truncated": False}

    truncated_text = text[:max_length]
    remaining_length = len(text) - max_length

    return {
        "content": truncated_text,
        "truncated": True,
        "original_length": len(text),
        "remaining_length": remaining_length,
        "suggestion": f"Content was truncated. {remaining_length} characters remaining. Use specific search parameters to reduce results.",
    }
