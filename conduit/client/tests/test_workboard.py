"""
Simplified Workboard tests focusing on existing functionality.

This module tests the Workboard functionality that currently works:
1. Column search operations (project.column.search)
2. Task search with column constraints (maniphest.search with columnPHIDs)
3. Column transaction creation (maniphest.create_column_transaction)
4. Task-column attachment data structure
"""

import time
import unittest

from conduit.client.project import ProjectClient
from conduit.client.maniphest import ManiphestClient


class TestWorkboardExistingFeatures(unittest.TestCase):
    """Test existing Workboard features that are currently functional."""

    def setUp(self):
        """Set up test environment with clients."""
        # Use environment variables for configuration
        import os

        api_url = os.getenv("PHABRICATOR_URL", "http://127.0.0.1:8080/api/")
        api_token = os.getenv("PHABRICATOR_TOKEN")

        if not api_token:
            self.skipTest("PHABRICATOR_TOKEN environment variable not set")

        self.project_client = ProjectClient(api_url, api_token)
        self.maniphest_client = ManiphestClient(api_url, api_token)
        self.test_project_prefix = f"workboard_test_{int(time.time())}"

    def test_column_search_functionality(self):
        """Test project column search functionality."""
        # Create a test project
        project_result = self.project_client.create_project(
            name=f"{self.test_project_prefix}_column_search",
            description="Project for testing column search",
        )
        project_phid = project_result["object"]["phid"]

        # Test 1: Search all columns
        all_columns = self.project_client.search_columns(limit=10)
        self.assertIn("data", all_columns)
        self.assertIn("cursor", all_columns)
        self.assertIsInstance(all_columns["data"], list)

        # Test 2: Search columns for specific project
        project_columns = self.project_client.search_columns(
            constraints={"projects": [project_phid]}, limit=10
        )
        self.assertIn("data", project_columns)
        self.assertIsInstance(project_columns["data"], list)

        # Test 3: Verify column structure if any exist
        if all_columns["data"]:
            column = all_columns["data"][0]
            self._validate_column_structure(column)

    def test_task_search_with_column_constraints(self):
        """Test searching tasks with column-related constraints."""
        # Test 1: Search tasks with column attachments
        tasks_result = self.maniphest_client.search_tasks(
            constraints={}, attachments={"columns": True}, limit=5
        )

        self.assertIn("data", tasks_result)
        self.assertIsInstance(tasks_result["data"], list)

        # Verify column attachment structure for each task
        for task in tasks_result["data"]:
            if "attachments" in task and "columns" in task["attachments"]:
                column_attachment = task["attachments"]["columns"]
                self._validate_column_attachment_structure(column_attachment)

        # Test 2: Search by non-existent column (should return empty)
        empty_result = self.maniphest_client.search_tasks(
            constraints={"columnPHIDs": ["PHID-PCOL-NONEXISTENT"]}, limit=10
        )

        self.assertEqual(len(empty_result["data"]), 0)
        self.assertIn("cursor", empty_result)

    def test_column_transaction_creation(self):
        """Test creation of column transactions for task movement."""
        # Test 1: Simple column transaction
        simple_tx = self.maniphest_client.create_column_transaction(
            column_phid="PHID-PCOL-EXAMPLE"
        )
        self.assertEqual(simple_tx["type"], "column")
        self.assertEqual(simple_tx["value"], ["PHID-PCOL-EXAMPLE"])

        # Test 2: Column transaction with positioning
        positioned_tx = self.maniphest_client.create_column_transaction(
            column_phid="PHID-PCOL-EXAMPLE",
            before_phid="PHID-TASK-BEFORE1",
            after_phid="PHID-TASK-AFTER1",
        )
        self.assertEqual(positioned_tx["type"], "column")
        self.assertIsInstance(positioned_tx["value"], list)
        self.assertEqual(len(positioned_tx["value"]), 1)

        column_position = positioned_tx["value"][0]
        self.assertEqual(column_position["columnPHID"], "PHID-PCOL-EXAMPLE")
        self.assertEqual(column_position["beforePHID"], "PHID-TASK-BEFORE1")
        self.assertEqual(column_position["afterPHID"], "PHID-TASK-AFTER1")

        # Test 3: Multiple column transaction formats
        # Test with just after_phid
        after_only_tx = self.maniphest_client.create_column_transaction(
            column_phid="PHID-PCOL-EXAMPLE", after_phid="PHID-TASK-AFTER1"
        )
        self.assertEqual(after_only_tx["type"], "column")
        self.assertIsInstance(after_only_tx["value"], list)
        self.assertEqual(len(after_only_tx["value"]), 1)
        self.assertEqual(after_only_tx["value"][0]["columnPHID"], "PHID-PCOL-EXAMPLE")
        self.assertEqual(after_only_tx["value"][0]["afterPHID"], "PHID-TASK-AFTER1")

        # Test with just before_phid
        before_only_tx = self.maniphest_client.create_column_transaction(
            column_phid="PHID-PCOL-EXAMPLE", before_phid="PHID-TASK-BEFORE1"
        )
        self.assertEqual(before_only_tx["type"], "column")
        self.assertIsInstance(before_only_tx["value"], list)
        self.assertEqual(len(before_only_tx["value"]), 1)
        self.assertEqual(before_only_tx["value"][0]["columnPHID"], "PHID-PCOL-EXAMPLE")
        self.assertEqual(before_only_tx["value"][0]["beforePHID"], "PHID-TASK-BEFORE1")

    def test_workboard_data_structures(self):
        """Test Workboard-related data structures and API responses."""
        # Create a test project
        project_result = self.project_client.create_project(
            name=f"{self.test_project_prefix}_data_structures",
            description="Project for testing data structures",
        )
        project_phid = project_result["object"]["phid"]

        # Test 1: Project column search response structure
        columns_result = self.project_client.search_columns(
            constraints={"projects": [project_phid]}, limit=5
        )

        expected_response_keys = ["data", "cursor", "maps", "query"]
        for key in expected_response_keys:
            self.assertIn(key, columns_result)

        # Test 2: Task search with columns attachment structure
        tasks_result = self.maniphest_client.search_tasks(
            constraints={"projects": [project_phid]},
            attachments={"columns": True},
            limit=5,
        )

        self.assertIn("data", tasks_result)
        self.assertIn("cursor", tasks_result)

        # Verify task data structure
        for task in tasks_result["data"]:
            self.assertIn("id", task)
            self.assertIn("phid", task)
            self.assertIn("fields", task)

            # Check for columns attachment
            if "attachments" in task:
                self.assertIn("columns", task["attachments"])

    def _validate_column_structure(self, column):
        """Helper method to validate column object structure."""
        # Basic column fields
        self.assertIn("id", column)
        self.assertIn("phid", column)
        self.assertIn("fields", column)

        # Column fields
        fields = column["fields"]
        self.assertIsInstance(fields, dict)

        # Common field names (may vary by Phabricator version)
        possible_fields = ["name", "projectPHID", "proxyPHID", "sequence", "isDefault"]
        found_fields = [field for field in possible_fields if field in fields]
        self.assertGreater(
            len(found_fields), 0, "Column should have at least one known field"
        )

        # PHID format validation
        self.assertTrue(column["phid"].startswith("PHID-"))

        # ID validation
        self.assertIsInstance(column["id"], str)

    def _validate_column_attachment_structure(self, column_attachment):
        """Helper method to validate column attachment structure."""
        expected_fields = ["columnPHIDs", "viewerCanEdit"]

        for field in expected_fields:
            if field in column_attachment:
                self.assertIsNotNone(column_attachment[field])

        # If columnPHIDs is present, it should be a list
        if "columnPHIDs" in column_attachment:
            self.assertIsInstance(column_attachment["columnPHIDs"], list)

        # If viewerCanEdit is present, it should be a boolean
        if "viewerCanEdit" in column_attachment:
            self.assertIsInstance(column_attachment["viewerCanEdit"], bool)


if __name__ == "__main__":
    unittest.main()
