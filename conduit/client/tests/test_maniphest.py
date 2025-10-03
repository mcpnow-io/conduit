from unittest import TestCase

from conduit.client.base import PhabricatorAPIError
from conduit.client.maniphest import ManiphestClient
from conduit.client.types import (
    ManiphestSearchAttachments,
    ManiphestSearchConstraints,
    ManiphestTaskInfo,
    ManiphestTaskTransactionComment,
    ManiphestTaskTransactionDescription,
    ManiphestTaskTransactionOwner,
    ManiphestTaskTransactionParentsAdd,
    ManiphestTaskTransactionParentsRemove,
    ManiphestTaskTransactionParentsSet,
    ManiphestTaskTransactionPriority,
    ManiphestTaskTransactionStatus,
    ManiphestTaskTransactionSubtasksAdd,
    ManiphestTaskTransactionSubtasksRemove,
    ManiphestTaskTransactionSubtasksSet,
    ManiphestTaskTransactionTitle,
    UserInfo,
)
from conduit.client.user import UserClient
from conduit.conduit import get_config


class TestManiphestClient(TestCase):
    def setUp(self):
        super().setUp()
        config = get_config()
        self.cli = ManiphestClient(config.url, config.token)

        self.user: UserInfo = UserClient(config.url, config.token).whoami()

        self.task: ManiphestTaskInfo = self.cli.create_task("Test")
        self.task2: ManiphestTaskInfo = self.cli.create_task("Test2")

    def test_get_task(self):
        with self.subTest("Get existing task"):
            self.cli.get_task(self.task["id"])

        with self.subTest("Get non-existing Task"):
            with self.assertRaises(PhabricatorAPIError):
                self.cli.get_task(0)

    def test_edi_task_metadata(self):
        with self.subTest("update title"):
            self.cli.edit_task(
                object_identifier=self.task["id"],
                transactions=[
                    ManiphestTaskTransactionTitle(
                        type="title",
                        value="Updated Title",
                    )
                ],
            )

        with self.subTest("update owner"):
            self.cli.edit_task(
                object_identifier=self.task["id"],
                transactions=[
                    ManiphestTaskTransactionOwner(
                        type="owner",
                        value=self.user["phid"],
                    )
                ],
            )

        with self.subTest("update status"):
            self.cli.edit_task(
                object_identifier=self.task["id"],
                transactions=[
                    ManiphestTaskTransactionStatus(
                        type="status",
                        value="resolved",
                    )
                ],
            )

        with self.subTest("update priority"):
            self.cli.edit_task(
                object_identifier=self.task["id"],
                transactions=[
                    ManiphestTaskTransactionPriority(
                        type="priority",
                        value="high",
                    )
                ],
            )

        with self.subTest("update description"):
            self.cli.edit_task(
                object_identifier=self.task["id"],
                transactions=[
                    ManiphestTaskTransactionDescription(
                        type="description",
                        value="Updated Description",
                    )
                ],
            )

    def test_edit_task_add_commits(self):
        with self.subTest("add commits"):
            self.cli.edit_task(
                object_identifier=self.task["id"],
                transactions=[
                    ManiphestTaskTransactionComment(
                        type="comment",
                        value="Added commits to the task.",
                    )
                ],
            )

    def test_edit_task_subtask_parent(self):
        self.cli.edit_task(
            object_identifier=self.task["id"],
            transactions=[
                ManiphestTaskTransactionSubtasksAdd(
                    type="subtasks.add",
                    value=[self.task2["phid"]],
                )
            ],
        )

        self.cli.edit_task(
            object_identifier=self.task["id"],
            transactions=[
                ManiphestTaskTransactionSubtasksRemove(
                    type="subtasks.remove",
                    value=[self.task2["phid"]],
                )
            ],
        )

        # subtask remove is idempotent
        self.cli.edit_task(
            object_identifier=self.task["id"],
            transactions=[
                ManiphestTaskTransactionSubtasksRemove(
                    type="subtasks.remove",
                    value=[self.task2["phid"]],
                )
            ],
        )

        self.cli.edit_task(
            object_identifier=self.task["id"],
            transactions=[
                ManiphestTaskTransactionSubtasksSet(
                    type="subtasks.set",
                    value=[self.task2["phid"]],
                )
            ],
        )

    def test_edit_task_parent(self):
        self.cli.edit_task(
            object_identifier=self.task["id"],
            transactions=[
                ManiphestTaskTransactionParentsAdd(
                    type="parents.add",
                    value=[self.task2["phid"]],
                )
            ],
        )

        self.cli.edit_task(
            object_identifier=self.task["id"],
            transactions=[
                ManiphestTaskTransactionParentsRemove(
                    type="parents.remove",
                    value=[self.task2["phid"]],
                )
            ],
        )

        # parent remove is idempotent
        self.cli.edit_task(
            object_identifier=self.task["id"],
            transactions=[
                ManiphestTaskTransactionParentsRemove(
                    type="parents.remove",
                    value=[self.task2["phid"]],
                )
            ],
        )

        self.cli.edit_task(
            object_identifier=self.task["id"],
            transactions=[
                ManiphestTaskTransactionParentsSet(
                    type="parents.set",
                    value=[self.task2["phid"]],
                )
            ],
        )

    def test_search_tasks(self):
        """Test various search functionality"""

        with self.subTest("Search all tasks"):
            results = self.cli.search_tasks()
            self.assertIsInstance(results, dict)
            self.assertIn("data", results)
            self.assertIn("cursor", results)
            # Should find at least our created tasks
            self.assertGreaterEqual(len(results.get("data", [])), 2)

        with self.subTest("Search with query key"):
            results = self.cli.search_tasks(query_key="all")
            self.assertIsInstance(results, dict)
            self.assertIn("data", results)
            # Should find at least our created tasks
            self.assertGreaterEqual(len(results.get("data", [])), 2)

        with self.subTest("Search with constraints"):
            constraints: ManiphestSearchConstraints = {"statuses": ["open"]}
            results = self.cli.search_tasks(constraints=constraints)
            self.assertIsInstance(results, dict)
            # Should find at least our created tasks (they are open by default)
            self.assertGreaterEqual(len(results.get("data", [])), 2)

        with self.subTest("Search with attachments"):
            attachments: ManiphestSearchAttachments = {
                "subscribers": True,
                "projects": True,
            }
            results = self.cli.search_tasks(attachments=attachments, limit=1)
            self.assertIsInstance(results, dict)
            if results.get("data"):
                # Check if attachments are present
                task = results["data"][0]
                self.assertIn("attachments", task)

        with self.subTest("Search with ordering"):
            results = self.cli.search_tasks(order="newest", limit=5)
            self.assertIsInstance(results, dict)
            # Should find at least our recently created tasks
            self.assertGreaterEqual(len(results.get("data", [])), 2)

        with self.subTest("Search with limit"):
            results = self.cli.search_tasks(limit=1)
            self.assertIsInstance(results, dict)
            self.assertLessEqual(len(results.get("data", [])), 1)

        with self.subTest("Search by specific task IDs"):
            # Test searching for our specific created tasks
            constraints: ManiphestSearchConstraints = {
                "ids": [int(self.task["id"]), int(self.task2["id"])]
            }
            results = self.cli.search_tasks(constraints=constraints)
            self.assertIsInstance(results, dict)
            # Should find exactly our 2 tasks
            self.assertEqual(len(results.get("data", [])), 2)

            # Verify the returned tasks are actually our tasks
            found_ids = {task["id"] for task in results["data"]}
            expected_ids = {int(self.task["id"]), int(self.task2["id"])}
            self.assertEqual(found_ids, expected_ids)

            # Verify task structure matches API response
            for task in results["data"]:
                self.assertIn("type", task)
                self.assertEqual(task["type"], "TASK")
                self.assertIn("fields", task)
                self.assertIn("name", task["fields"])  # Task title is in "name" field
                self.assertIn("authorPHID", task["fields"])
                self.assertIn("status", task["fields"])
                self.assertIn("priority", task["fields"])

                # Additional validation of field structures
                status = task["fields"]["status"]
                self.assertIn("value", status)
                self.assertIn("name", status)

                # Verify priority structure
                priority = task["fields"]["priority"]
                self.assertIn("value", priority)
                self.assertIn("name", priority)

                # Verify description structure
                description = task["fields"]["description"]
                self.assertIsInstance(description, dict)
                self.assertIn("raw", description)

                # Verify the task names match what we created
                task_name = task["fields"]["name"]
                self.assertIn(task_name, ["Test", "Test2"])  # Our created task titles

                # Verify author is current user
                self.assertEqual(task["fields"]["authorPHID"], self.user["phid"])

    def test_search_helper_methods(self):
        """Test helper search methods"""

        with self.subTest("Search open tasks"):
            results = self.cli.search_open_tasks(limit=5)
            self.assertIsInstance(results, dict)
            # Should find at least our created tasks (they are open by default)
            self.assertGreaterEqual(len(results.get("data", [])), 2)

        with self.subTest("Search assigned tasks"):
            results = self.cli.search_assigned_tasks(limit=5)
            self.assertIsInstance(results, dict)
            # Might be 0 if no tasks are assigned to current user

        with self.subTest("Search authored tasks"):
            results = self.cli.search_authored_tasks(limit=5)
            self.assertIsInstance(results, dict)
            # Should find at least our created tasks
            self.assertGreaterEqual(len(results.get("data", [])), 2)

        with self.subTest("Search by status"):
            results = self.cli.search_tasks_by_status(["open"], limit=5)
            self.assertIsInstance(results, dict)
            # Should find at least our created tasks (they are open by default)
            self.assertGreaterEqual(len(results.get("data", [])), 2)

        with self.subTest("Search by assignee"):
            results = self.cli.search_tasks_by_assignee([self.user["phid"]], limit=5)
            self.assertIsInstance(results, dict)
            # Might be 0 if no tasks are assigned to current user

        with self.subTest("Fulltext search"):
            results = self.cli.fulltext_search_tasks("test", limit=5)
            self.assertIsInstance(results, dict)
            # Fulltext search might not find results immediately due to indexing delays
            # So we just verify the API call works without asserting result count

        with self.subTest("Search by author PHID"):
            # Test searching for tasks authored by current user
            results = self.cli.search_tasks(
                constraints={"authorPHIDs": [self.user["phid"]]}, limit=10
            )
            self.assertIsInstance(results, dict)
            # Should find at least our created tasks
            self.assertGreaterEqual(len(results.get("data", [])), 2)

            # Verify all returned tasks are authored by current user
            for task in results["data"]:
                self.assertEqual(task["fields"]["authorPHID"], self.user["phid"])
