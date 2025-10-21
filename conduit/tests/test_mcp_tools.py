#!/usr/bin/env python3
"""
Unit tests for MCP tools in main_tools.py

This module tests the MCP tool functions, particularly the modified
pha_diff_get and pha_diff_get_content methods.
"""

import time
import unittest
from unittest.mock import Mock, patch

from conduit.main_tools import register_tools
from conduit.client.unified import PhabricatorClient
from conduit.conduit import get_config


class TestMCPTools(unittest.TestCase):
    """Test MCP tool functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = get_config()
        self.client = PhabricatorClient(self.config.url, self.config.token)

        # Create test data for testing
        self.test_revision_id = None
        self.test_diff_phids = []
        self._setup_test_data()

    def _setup_test_data(self):
        """Create test revision with multiple diffs for testing."""
        try:
            # Create first diff
            diff1_content = """diff --git a/mcp_tools_test.txt b/mcp_tools_test.txt
new file mode 100644
index 0000000..8b13789
--- /dev/null
+++ b/mcp_tools_test.txt
@@ -0,0 +1 @@
+# Initial version for MCP tools testing
"""

            diff1_result = self.client.differential.create_raw_diff(diff=diff1_content)
            diff1_phid = diff1_result.get("phid")
            self.test_diff_phids.append(diff1_phid)

            # Create revision with first diff
            revision_result = self.client.differential.edit_revision(
                transactions=[
                    {
                        "type": "title",
                        "value": f"MCP Tools Test Revision {int(time.time())}",
                    },
                    {
                        "type": "summary",
                        "value": "Test revision for MCP tools unit testing",
                    },
                    {"type": "testPlan", "value": "Verify MCP tools functionality"},
                    {"type": "update", "value": diff1_phid},
                ]
            )

            if "object" in revision_result:
                self.test_revision_id = revision_result["object"]["id"]
                revision_phid = revision_result["object"]["phid"]

                # Create second diff (update)
                time.sleep(1)  # Ensure different timestamp
                diff2_content = """diff --git a/mcp_tools_test.txt b/mcp_tools_test.txt
new file mode 100644
index 0000000..557db03
--- /dev/null
+++ b/mcp_tools_test.txt
@@ -0,0 +1 @@
+# Updated version for MCP tools testing
"""

                diff2_result = self.client.differential.create_raw_diff(
                    diff=diff2_content
                )
                diff2_phid = diff2_result.get("phid")
                self.test_diff_phids.append(diff2_phid)

                # Update revision with second diff
                self.client.differential.edit_revision(
                    transactions=[
                        {"type": "update", "value": diff2_phid},
                        {
                            "type": "comment",
                            "value": "Updated with second diff for testing",
                        },
                    ],
                    object_identifier=revision_phid,
                )

        except Exception as e:
            print(f"Warning: Failed to create test data: {e}")

    def test_register_tools_function_exists(self):
        """Test that register_tools function exists and is callable."""
        self.assertTrue(callable(register_tools))

    def test_pha_diff_get_with_all_diffs(self):
        """Test pha_diff_get returns all diffs associated with a revision."""
        if not self.test_revision_id:
            self.skipTest("No test revision available")

        # Mock MCP instance
        mock_mcp = Mock()

        def get_client_func():
            return self.client

        # Register tools to get access to pha_diff_get
        register_tools(mock_mcp, get_client_func)

        # Get the registered pha_diff_get tool
        tool_calls = [
            call
            for call in mock_mcp.tool.call_args_list
            if call[1].get("name") == "pha_diff_get"
        ]

        if tool_calls:
            pha_diff_get_func = tool_calls[0][1]["func"]

            # Test the function
            result = pha_diff_get_func({"revision_id": f"D{self.test_revision_id}"})

            self.assertTrue(
                result.get("success"), f"pha_diff_get failed: {result.get('error')}"
            )
            self.assertIn("revision", result)

            revision = result["revision"]
            self.assertIn("all_diffs", revision)
            self.assertIsInstance(revision["all_diffs"], list)

            # Should have at least 2 diffs (initial + update)
            self.assertGreaterEqual(
                len(revision["all_diffs"]), 2, "Expected at least 2 diffs in all_diffs"
            )

            # Current diffPHID should be in all_diffs
            current_diff_phid = revision["fields"]["diffPHID"]
            found_current = any(
                diff["phid"] == current_diff_phid for diff in revision["all_diffs"]
            )
            self.assertTrue(found_current, "Current diffPHID not found in all_diffs")

            # All diffs should have required fields
            for diff in revision["all_diffs"]:
                self.assertIn("id", diff)
                self.assertIn("phid", diff)
                self.assertIsInstance(diff["id"], int)
                self.assertIsInstance(diff["phid"], str)
                self.assertTrue(diff["phid"].startswith("PHID-DIFF-"))

    def test_pha_diff_get_content_with_valid_phid(self):
        """Test pha_diff_get_content with valid PHID."""
        if not self.test_diff_phids:
            self.skipTest("No test diffs available")

        # Mock MCP instance
        mock_mcp = Mock()

        def get_client_func():
            return self.client

        # Register tools to get access to pha_diff_get_content
        register_tools(mock_mcp, get_client_func)

        # Get the registered pha_diff_get_content tool
        tool_calls = [
            call
            for call in mock_mcp.tool.call_args_list
            if call[1].get("name") == "pha_diff_get_content"
        ]

        if tool_calls:
            pha_diff_get_content_func = tool_calls[0][1]["func"]

            # Test with a valid PHID
            test_phid = self.test_diff_phids[0]
            result = pha_diff_get_content_func({"diff_phid": test_phid})

            self.assertTrue(
                result.get("success"),
                f"pha_diff_get_content failed: {result.get('error')}",
            )
            self.assertIn("diff_content", result)
            self.assertIsInstance(result["diff_content"], str)
            self.assertGreater(len(result["diff_content"]), 0)

    def test_pha_diff_get_content_error_handling(self):
        """Test pha_diff_get_content error handling."""
        # Mock MCP instance
        mock_mcp = Mock()

        def get_client_func():
            return self.client

        # Register tools to get access to pha_diff_get_content
        register_tools(mock_mcp, get_client_func)

        # Get the registered pha_diff_get_content tool
        tool_calls = [
            call
            for call in mock_mcp.tool.call_args_list
            if call[1].get("name") == "pha_diff_get_content"
        ]

        if tool_calls:
            pha_diff_get_content_func = tool_calls[0][1]["func"]

            # Test with invalid PHID format
            result = pha_diff_get_content_func({"diff_phid": "invalid_format"})
            self.assertFalse(result.get("success"))
            self.assertEqual(result.get("error_code"), "INVALID_PHID_FORMAT")
            self.assertIn("Invalid diff PHID format", result.get("error"))

            # Test with non-existent PHID
            result = pha_diff_get_content_func(
                {"diff_phid": "PHID-DIFF-nonexistent1234567890"}
            )
            self.assertFalse(result.get("success"))
            self.assertEqual(result.get("error_code"), "DIFF_NOT_FOUND")
            self.assertIn("Diff not found", result.get("error"))

    def test_pha_diff_get_error_handling(self):
        """Test pha_diff_get error handling."""
        # Mock MCP instance
        mock_mcp = Mock()

        def get_client_func():
            return self.client

        # Register tools to get access to pha_diff_get
        register_tools(mock_mcp, get_client_func)

        # Get the registered pha_diff_get tool
        tool_calls = [
            call
            for call in mock_mcp.tool.call_args_list
            if call[1].get("name") == "pha_diff_get"
        ]

        if tool_calls:
            pha_diff_get_func = tool_calls[0][1]["func"]

            # Test with non-existent revision
            result = pha_diff_get_func({"revision_id": "D99999"})
            self.assertFalse(result.get("success"))
            self.assertIn("not found", result.get("error"))

    def test_pha_diff_get_content_workflow_integration(self):
        """Test complete workflow: pha_diff_get -> pha_diff_get_content."""
        if not self.test_revision_id or not self.test_diff_phids:
            self.skipTest("No test data available")

        # Mock MCP instance
        mock_mcp = Mock()

        def get_client_func():
            return self.client

        # Register tools
        register_tools(mock_mcp, get_client_func)

        # Get both tools
        tool_calls = {
            call[1].get("name"): call[1]["func"]
            for call in mock_mcp.tool.call_args_list
            if call[1].get("name") in ["pha_diff_get", "pha_diff_get_content"]
        }

        if "pha_diff_get" in tool_calls and "pha_diff_get_content" in tool_calls:
            pha_diff_get_func = tool_calls["pha_diff_get"]
            pha_diff_get_content_func = tool_calls["pha_diff_get_content"]

            # Step 1: Get revision info
            rev_result = pha_diff_get_func({"revision_id": f"D{self.test_revision_id}"})
            self.assertTrue(rev_result.get("success"))

            # Step 2: Extract current diff PHID
            current_diff_phid = rev_result["revision"]["fields"]["diffPHID"]

            # Step 3: Get diff content using PHID
            content_result = pha_diff_get_content_func({"diff_phid": current_diff_phid})
            self.assertTrue(content_result.get("success"))
            self.assertIn("diff_content", content_result)

            # Step 4: Verify content is expected diff format
            diff_content = content_result["diff_content"]
            self.assertIn("diff --git", diff_content)

    def test_all_diffs_content_access(self):
        """Test that all diffs in all_diffs can be accessed via pha_diff_get_content."""
        if not self.test_revision_id:
            self.skipTest("No test revision available")

        # Mock MCP instance
        mock_mcp = Mock()

        def get_client_func():
            return self.client

        # Register tools
        register_tools(mock_mcp, get_client_func)

        # Get both tools
        tool_calls = {
            call[1].get("name"): call[1]["func"]
            for call in mock_mcp.tool.call_args_list
            if call[1].get("name") in ["pha_diff_get", "pha_diff_get_content"]
        }

        if "pha_diff_get" in tool_calls and "pha_diff_get_content" in tool_calls:
            pha_diff_get_func = tool_calls["pha_diff_get"]
            pha_diff_get_content_func = tool_calls["pha_diff_get_content"]

            # Get revision with all diffs
            rev_result = pha_diff_get_func({"revision_id": f"D{self.test_revision_id}"})
            self.assertTrue(rev_result.get("success"))

            all_diffs = rev_result["revision"]["all_diffs"]

            # Test that each diff can be accessed
            for diff in all_diffs:
                diff_phid = diff["phid"]
                content_result = pha_diff_get_content_func({"diff_phid": diff_phid})
                self.assertTrue(
                    content_result.get("success"),
                    f"Failed to get content for diff {diff_phid}",
                )
                self.assertIn("diff_content", content_result)


class TestMCPToolsMocked(unittest.TestCase):
    """Test MCP tools with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures with mocks."""
        self.mock_mcp = Mock()
        self.mock_client = Mock()

    def test_tool_registration(self):
        """Test that tools are properly registered with expected signatures."""

        def get_client_func():
            return self.mock_client

        # This should not raise an exception
        try:
            register_tools(self.mock_mcp, get_client_func)
            self.assertTrue(self.mock_mcp.tool.called)
        except Exception as e:
            self.fail(f"register_tools raised an exception: {e}")

    @patch("conduit.main_tools.handle_api_errors")
    def test_tool_decorators(self, mock_handle_errors):
        """Test that tools have proper decorators applied."""

        def get_client_func():
            return self.mock_client

        register_tools(self.mock_mcp, get_client_func)

        # Verify that handle_api_errors was called (tools were decorated)
        self.assertTrue(mock_handle_errors.called)


if __name__ == "__main__":
    unittest.main()
