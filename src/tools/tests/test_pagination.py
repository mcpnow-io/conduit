"""Tests for pagination utilities."""

from src.tools.pagination import (
    _add_pagination_metadata,
    _apply_smart_pagination,
    _truncate_text_response,
)


class TestPaginationMetadata:
    """Test pagination metadata functions."""

    def test_add_pagination_metadata_with_cursor(self):
        """Test adding pagination metadata with cursor."""
        result = {"data": [1, 2, 3]}
        cursor = {"after": "token123", "limit": 50}

        enhanced_result = _add_pagination_metadata(result, cursor)

        assert "pagination" in enhanced_result
        assert enhanced_result["pagination"]["cursor"] == cursor
        assert enhanced_result["pagination"]["has_more"] is True
        assert enhanced_result["pagination"]["limit"] == 50

    def test_add_pagination_metadata_without_cursor(self):
        """Test adding pagination metadata without cursor."""
        result = {"data": [1, 2, 3]}

        enhanced_result = _add_pagination_metadata(result)

        assert "pagination" not in enhanced_result

    def test_add_pagination_metadata_with_empty_cursor(self):
        """Test adding pagination metadata with empty cursor."""
        result = {"data": [1, 2, 3]}
        cursor = {"after": None, "limit": 100}

        enhanced_result = _add_pagination_metadata(result, cursor)

        assert "pagination" in enhanced_result
        assert enhanced_result["pagination"]["has_more"] is False


class TestSmartPagination:
    """Test smart pagination functions."""

    def test_apply_smart_pagination_no_limit_needed(self):
        """Test pagination when data is within limit."""
        data = [1, 2, 3]

        result = _apply_smart_pagination(data, limit=10)

        assert result["data"] == [1, 2, 3]
        assert result["pagination"]["total"] == 3
        assert result["pagination"]["returned"] == 3
        assert result["pagination"]["has_more"] is False
        assert result["suggestion"] is None

    def test_apply_smart_pagination_with_limit(self):
        """Test pagination when data exceeds limit."""
        data = list(range(15))

        result = _apply_smart_pagination(data, limit=5)

        assert result["data"] == [0, 1, 2, 3, 4]
        assert result["pagination"]["total"] == 15
        assert result["pagination"]["returned"] == 5
        assert result["pagination"]["has_more"] is True
        assert "Use pagination to retrieve remaining 10 items" in result["suggestion"]

    def test_apply_smart_pagination_default_limit(self):
        """Test pagination with default limit."""
        data = list(range(50))

        result = _apply_smart_pagination(data)

        assert len(result["data"]) == 50
        assert result["pagination"]["has_more"] is False

    def test_apply_smart_pagination_empty_data(self):
        """Test pagination with empty data."""
        data = []

        result = _apply_smart_pagination(data, limit=10)

        assert result["data"] == []
        assert result["pagination"]["total"] == 0
        assert result["pagination"]["returned"] == 0
        assert result["pagination"]["has_more"] is False


class TestTextTruncation:
    """Test text truncation functions."""

    def test_truncate_text_response_no_truncation(self):
        """Test text truncation when not needed."""
        text = "Short text"

        result = _truncate_text_response(text, max_length=50)

        assert result["content"] == "Short text"
        assert result["truncated"] is False

    def test_truncate_text_response_with_truncation(self):
        """Test text truncation when needed."""
        text = "A" * 100

        result = _truncate_text_response(text, max_length=50)

        assert len(result["content"]) == 50
        assert result["truncated"] is True
        assert result["original_length"] == 100
        assert result["remaining_length"] == 50
        assert "Content was truncated" in result["suggestion"]

    def test_truncate_text_response_default_length(self):
        """Test text truncation with default max length."""
        text = "A" * 1000

        result = _truncate_text_response(text)

        assert len(result["content"]) == 1000
        assert result["truncated"] is False

    def test_truncate_text_response_exact_length(self):
        """Test text truncation with exact length match."""
        text = "A" * 50

        result = _truncate_text_response(text, max_length=50)

        assert result["content"] == text
        assert result["truncated"] is False

    def test_truncate_text_response_empty_string(self):
        """Test text truncation with empty string."""
        text = ""

        result = _truncate_text_response(text, max_length=50)

        assert result["content"] == ""
        assert result["truncated"] is False
