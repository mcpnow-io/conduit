"""Tests for optimization utilities."""

from conduit.tools.optimization import (
    optimize_large_text,
    optimize_search_results,
    optimize_token_usage,
)


class TestOptimizeTokenUsage:
    """Test token usage optimization decorator."""

    def test_optimize_token_usage_with_large_data(self):
        """Test decorator with large dataset."""

        @optimize_token_usage
        def mock_search_function(limit=100):
            return {"data": list(range(100)), "cursor": "token123"}

        result = mock_search_function(limit=50)

        assert "data" in result
        assert "pagination" in result
        assert result["pagination"]["has_more"] is True
        assert result["pagination"]["total"] == 100

    def test_optimize_token_usage_with_small_data(self):
        """Test decorator with small dataset."""

        @optimize_token_usage
        def mock_search_function():
            return {"data": [1, 2, 3]}

        result = mock_search_function()

        assert result["data"] == [1, 2, 3]
        assert "pagination" not in result

    def test_optimize_token_usage_without_data(self):
        """Test decorator with no data field."""

        @optimize_token_usage
        def mock_function():
            return {"message": "success"}

        result = mock_function()

        assert result == {"message": "success"}

    def test_optimize_token_usage_with_non_dict_result(self):
        """Test decorator with non-dict result."""

        @optimize_token_usage
        def mock_function():
            return "simple string"

        result = mock_function()

        assert result == "simple string"

    def test_optimize_token_usage_with_empty_data(self):
        """Test decorator with empty data list."""

        @optimize_token_usage
        def mock_function():
            return {"data": []}

        result = mock_function()

        assert result["data"] == []


class TestOptimizeSearchResults:
    """Test search results optimization."""

    def test_optimize_search_results_with_large_data(self):
        """Test optimization with large dataset."""
        result = {"data": list(range(50)), "cursor": "token123"}

        optimized = optimize_search_results(result, max_tokens=5000)

        assert len(optimized["data"]) == 20
        assert "token_optimization" in optimized
        assert optimized["token_optimization"]["applied"] is True
        assert optimized["token_optimization"]["original_count"] == 50
        assert optimized["token_optimization"]["returned_count"] == 20

    def test_optimize_search_results_with_small_data(self):
        """Test optimization with small dataset."""
        result = {"data": [1, 2, 3]}

        optimized = optimize_search_results(result, max_tokens=5000)

        assert optimized["data"] == [1, 2, 3]
        assert "token_optimization" not in optimized

    def test_optimize_search_results_without_max_tokens(self):
        """Test optimization without max_tokens."""
        result = {"data": list(range(50))}

        optimized = optimize_search_results(result, max_tokens=None)

        assert len(optimized["data"]) == 50
        assert "token_optimization" not in optimized

    def test_optimize_search_results_without_data(self):
        """Test optimization without data field."""
        result = {"message": "success"}

        optimized = optimize_search_results(result, max_tokens=5000)

        assert optimized == {"message": "success"}

    def test_optimize_search_results_with_empty_data(self):
        """Test optimization with empty data."""
        result = {"data": []}

        optimized = optimize_search_results(result, max_tokens=5000)

        assert optimized["data"] == []
        assert "token_optimization" not in optimized

    def test_optimize_search_results_with_non_list_data(self):
        """Test optimization with non-list data."""
        result = {"data": "not a list"}

        optimized = optimize_search_results(result, max_tokens=5000)

        assert optimized["data"] == "not a list"
        assert "token_optimization" not in optimized


class TestOptimizeLargeText:
    """Test large text optimization."""

    def test_optimize_large_text_short(self):
        """Test optimization with short text."""
        text = "Short text"

        result = optimize_large_text(text, max_length=50)

        assert result["content"] == "Short text"
        assert result["truncated"] is False

    def test_optimize_large_text_long(self):
        """Test optimization with long text."""
        text = "A" * 100

        result = optimize_large_text(text, max_length=50)

        assert len(result["content"]) == 50
        assert result["truncated"] is True
        assert result["original_length"] == 100
        assert result["remaining_length"] == 50

    def test_optimize_large_text_default_length(self):
        """Test optimization with default max length."""
        text = "A" * 1000

        result = optimize_large_text(text)

        assert len(result["content"]) == 1000
        assert result["truncated"] is False

    def test_optimize_large_text_empty(self):
        """Test optimization with empty text."""
        text = ""

        result = optimize_large_text(text)

        assert result["content"] == ""
        assert result["truncated"] is False
