#!/usr/bin/env python3

import os
import sys
import unittest
from unittest.mock import Mock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from conduit.client.base import BasePhabricatorClient
from conduit.utils import RuntimeValidationClient
from conduit.client.unified import (
    ClientConfig,
    PhabricatorClient,
)
from conduit.main_tools import handle_api_errors, register_tools
from conduit.utils import ErrorCode


class TestNewFeatures(unittest.TestCase):
    """Test new features implemented in the improvement plan."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_mcp = Mock()
        self.mock_client = Mock()

    def test_error_code_enum(self):
        """Test ErrorCode enum values."""
        self.assertEqual(ErrorCode.NETWORK_ERROR.value, "NETWORK_ERROR")
        self.assertEqual(ErrorCode.AUTH_ERROR.value, "AUTH_ERROR")
        self.assertEqual(ErrorCode.VALIDATION_ERROR.value, "VALIDATION_ERROR")
        self.assertEqual(ErrorCode.RATE_LIMIT_ERROR.value, "RATE_LIMIT_ERROR")
        self.assertEqual(ErrorCode.NOT_FOUND.value, "NOT_FOUND")
        self.assertEqual(ErrorCode.UNKNOWN_ERROR.value, "UNKNOWN_ERROR")

    def test_handle_api_errors_decorator(self):
        """Test the handle_api_errors decorator."""

        @handle_api_errors
        def test_function(success=True):
            if success:
                return {"data": "success"}
            else:
                raise ValueError("Test error")

        # Test successful execution
        result = test_function(success=True)
        self.assertEqual(result["success"], True)
        self.assertEqual(result["result"], {"data": "success"})

        # Test error handling
        result = test_function(success=False)
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error"], "Parameter validation failed: Test error")
        self.assertEqual(result["error_code"], "VALIDATION_ERROR")

    def test_enhanced_client_configuration(self):
        """Test EnhancedPhabricatorClient configuration."""

        # Test custom configuration triggers enhanced client
        client = PhabricatorClient(
            api_url="https://test.example.com/api/",
            api_token="test_token",
            timeout=60.0,
            max_retries=5,
            enable_cache=True,
        )

        # Check that enhanced features are enabled
        stats = client.get_stats()
        self.assertIn("config", stats)
        self.assertEqual(stats["config"]["timeout"], 60.0)
        self.assertEqual(stats["config"]["max_retries"], 5)
        self.assertEqual(stats["config"]["enable_cache"], True)

    def test_basic_client_configuration(self):
        """Test basic PhabricatorClient configuration."""

        # Test default configuration uses basic client
        client = PhabricatorClient(
            api_url="https://test.example.com/api/", api_token="test_token"
        )

        # Check that basic client is used
        stats = client.get_stats()
        self.assertIn("message", stats)
        self.assertIn("Basic client", stats["message"])

    def test_client_config_class(self):
        """Test ClientConfig class."""

        # Test default configuration
        config = ClientConfig()
        self.assertEqual(config.timeout, 30.0)
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.enable_cache, True)

        # Test custom configuration
        config = ClientConfig(
            timeout=60.0, max_retries=5, enable_cache=False, custom_param="test_value"
        )
        self.assertEqual(config.timeout, 60.0)
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.enable_cache, False)
        self.assertEqual(config.extra_config["custom_param"], "test_value")

    def test_type_safe_client_initialization(self):
        """Test TypeSafePhabricatorClient initialization."""

        # Create a mock base client
        mock_base_client = Mock(spec=BasePhabricatorClient)
        mock_base_client.user = Mock()
        mock_base_client.maniphest = Mock()

        # Create type-safe client
        type_safe_client = RuntimeValidationClient(mock_base_client)

        # Check that it was initialized correctly
        self.assertEqual(type_safe_client.base_client, mock_base_client)

    def test_register_tools_with_type_safety(self):
        """Test register_tools function with type safety option."""

        mock_get_client_func = Mock()
        mock_get_client_func.return_value = self.mock_client

        # This should not raise an exception
        try:
            register_tools(self.mock_mcp, mock_get_client_func, enable_type_safety=True)
        except Exception as e:
            self.fail(f"register_tools raised an exception: {e}")

    def test_token_optimization_decorator(self):
        """Test token optimization functionality."""

        from conduit.main_tools import _apply_smart_pagination

        # Test smart pagination
        test_data = list(range(100))
        result = _apply_smart_pagination(test_data, limit=20)

        self.assertEqual(result["data"], list(range(20)))
        self.assertEqual(result["pagination"]["total"], 100)
        self.assertEqual(result["pagination"]["returned"], 20)
        self.assertTrue(result["pagination"]["has_more"])
        self.assertIsNotNone(result["suggestion"])

    def test_pagination_metadata(self):
        """Test pagination metadata addition."""

        from conduit.main_tools import _add_pagination_metadata

        # Test with cursor
        result = {"data": [1, 2, 3]}
        cursor = {"limit": 100, "after": "cursor123"}

        enhanced_result = _add_pagination_metadata(result, cursor)

        self.assertIn("pagination", enhanced_result)
        self.assertEqual(enhanced_result["pagination"]["cursor"], cursor)
        self.assertTrue(enhanced_result["pagination"]["has_more"])

    def test_text_truncation(self):
        """Test text truncation functionality."""

        from conduit.main_tools import _truncate_text_response

        # Test short text (no truncation)
        short_text = "Hello, world!"
        result = _truncate_text_response(short_text, max_length=20)
        self.assertEqual(result["content"], short_text)
        self.assertFalse(result["truncated"])

        # Test long text (truncation)
        long_text = "A" * 3000
        result = _truncate_text_response(long_text, max_length=2000)
        self.assertEqual(len(result["content"]), 2000)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["original_length"], 3000)
        self.assertIsNotNone(result["suggestion"])

    def test_error_details_function(self):
        """Test _get_error_details function."""

        from conduit.utils import ErrorCode
        from conduit.tools.handlers import _get_error_details

        # Test network error
        network_error = ConnectionError("Network failed")
        details = _get_error_details(network_error)
        self.assertEqual(details["error_code"], ErrorCode.NETWORK_ERROR.value)
        self.assertIn("Check your network", details["suggestion"])

        # Test validation error
        value_error = ValueError("Invalid parameter")
        details = _get_error_details(value_error)
        self.assertEqual(details["error_code"], ErrorCode.VALIDATION_ERROR.value)
        self.assertIn("valid parameters", details["suggestion"])

    def test_tool_integration(self):
        """Test that tools are properly integrated."""

        # Test that tools have the expected decorators
        mock_get_client_func = Mock()
        mock_get_client_func.return_value = self.mock_client

        register_tools(self.mock_mcp, mock_get_client_func)

        # Check that tools were registered
        self.assertTrue(self.mock_mcp.tool.called)


class TestFeatureIntegration(unittest.TestCase):
    """Integration tests for feature combinations."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_mcp = Mock()
        self.mock_client = Mock()

    def test_error_handling_with_type_safety(self):
        """Test combination of error handling and type safety."""

        @handle_api_errors
        def test_function_with_types(data: dict) -> dict:
            if not isinstance(data, dict):
                raise ValueError("Expected dict")
            return {"result": data}

        # Test with valid data
        result = test_function_with_types({"key": "value"})
        self.assertEqual(result["success"], True)
        self.assertEqual(result["result"], {"result": {"key": "value"}})

        # Test with invalid data
        result = test_function_with_types("invalid")
        self.assertEqual(result["success"], False)
        self.assertEqual(result["error_code"], "VALIDATION_ERROR")

    def test_client_configuration_combinations(self):
        """Test different client configuration combinations."""

        # Test various configurations
        configs = [
            {"timeout": 30.0, "max_retries": 3},  # Basic client
            {"timeout": 60.0, "max_retries": 5},  # Enhanced client
            {
                "timeout": 45.0,
                "max_retries": 2,
                "enable_cache": False,
            },  # Custom enhanced
        ]

        for config in configs:
            client = PhabricatorClient(
                api_url="https://test.example.com/api/",
                api_token="test_token",
                **config,
            )

            # Should not raise exceptions
            stats = client.get_stats()
            self.assertIsInstance(stats, dict)


if __name__ == "__main__":
    unittest.main()
