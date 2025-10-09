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

    def test_create_column_transaction_type_consistency(self):
        """
        测试 create_column_transaction 方法始终返回正确的列表格式。

        这个测试专门针对修复的问题：
        API Error: Exception when processing transaction of type "column":
        Error while reading "value": Expected a list, but value is not a list.
        """
        test_column_phid = "PHID-PCOL-TESTCOLUMN"
        test_before_phid = "PHID-TASK-BEFORE"
        test_after_phid = "PHID-TASK-AFTER"

        with self.subTest("Simple column transaction (no positioning)"):
            """测试简单列事务始终返回列表格式"""
            transaction = self.cli.create_column_transaction(
                column_phid=test_column_phid
            )

            # 验证基本结构
            self.assertEqual(transaction["type"], "column")
            self.assertIsInstance(
                transaction["value"],
                list,
                "简单列事务的 value 必须是列表格式，不能是字符串",
            )
            self.assertEqual(len(transaction["value"]), 1, "列表应该只包含一个元素")

            # 验证列位置对象
            column_position = transaction["value"][0]
            self.assertIsInstance(column_position, dict, "列表元素应该是字典格式")
            self.assertEqual(
                column_position["columnPHID"],
                test_column_phid,
                "columnPHID 应该正确设置",
            )

            # 验证没有定位字段
            self.assertNotIn(
                "beforePHIDs", column_position, "简单列事务不应该包含 beforePHIDs"
            )
            self.assertNotIn(
                "afterPHIDs", column_position, "简单列事务不应该包含 afterPHIDs"
            )

        with self.subTest("Column transaction with before_phids only"):
            """测试只包含 before_phids 的列事务"""
            transaction = self.cli.create_column_transaction(
                column_phid=test_column_phid, before_phids=[test_before_phid]
            )

            # 验证基本结构
            self.assertEqual(transaction["type"], "column")
            self.assertIsInstance(
                transaction["value"], list, "带定位的列事务也必须是列表格式"
            )
            self.assertEqual(len(transaction["value"]), 1, "列表应该只包含一个元素")

            # 验证列位置对象
            column_position = transaction["value"][0]
            self.assertEqual(column_position["columnPHID"], test_column_phid)
            self.assertIn("beforePHIDs", column_position, "应该包含 beforePHIDs")
            self.assertEqual(
                column_position["beforePHIDs"],
                [test_before_phid],
                "beforePHIDs 应该正确设置",
            )
            self.assertNotIn("afterPHIDs", column_position, "不应该包含 afterPHIDs")

        with self.subTest("Column transaction with after_phids only"):
            """测试只包含 after_phids 的列事务"""
            transaction = self.cli.create_column_transaction(
                column_phid=test_column_phid, after_phids=[test_after_phid]
            )

            # 验证基本结构
            self.assertEqual(transaction["type"], "column")
            self.assertIsInstance(
                transaction["value"], list, "带定位的列事务也必须是列表格式"
            )
            self.assertEqual(len(transaction["value"]), 1, "列表应该只包含一个元素")

            # 验证列位置对象
            column_position = transaction["value"][0]
            self.assertEqual(column_position["columnPHID"], test_column_phid)
            self.assertNotIn("beforePHIDs", column_position, "不应该包含 beforePHIDs")
            self.assertIn("afterPHIDs", column_position, "应该包含 afterPHIDs")
            self.assertEqual(
                column_position["afterPHIDs"],
                [test_after_phid],
                "afterPHIDs 应该正确设置",
            )

        with self.subTest("Column transaction with both before_phids and after_phids"):
            """测试同时包含 before_phids 和 after_phids 的列事务"""
            transaction = self.cli.create_column_transaction(
                column_phid=test_column_phid,
                before_phids=[test_before_phid],
                after_phids=[test_after_phid],
            )

            # 验证基本结构
            self.assertEqual(transaction["type"], "column")
            self.assertIsInstance(
                transaction["value"], list, "完整定位的列事务也必须是列表格式"
            )
            self.assertEqual(len(transaction["value"]), 1, "列表应该只包含一个元素")

            # 验证列位置对象
            column_position = transaction["value"][0]
            self.assertEqual(column_position["columnPHID"], test_column_phid)
            self.assertIn("beforePHIDs", column_position, "应该包含 beforePHIDs")
            self.assertIn("afterPHIDs", column_position, "应该包含 afterPHIDs")
            self.assertEqual(
                column_position["beforePHIDs"],
                [test_before_phid],
                "beforePHIDs 应该正确设置",
            )
            self.assertEqual(
                column_position["afterPHIDs"],
                [test_after_phid],
                "afterPHIDs 应该正确设置",
            )

        with self.subTest("Column transaction with multiple positioning PHIDs"):
            """测试多个定位 PHID 的列事务"""
            multiple_before = ["PHID-TASK-BEFORE1", "PHID-TASK-BEFORE2"]
            multiple_after = ["PHID-TASK-AFTER1", "PHID-TASK-AFTER2"]

            transaction = self.cli.create_column_transaction(
                column_phid=test_column_phid,
                before_phids=multiple_before,
                after_phids=multiple_after,
            )

            # 验证基本结构
            self.assertEqual(transaction["type"], "column")
            self.assertIsInstance(transaction["value"], list)
            self.assertEqual(len(transaction["value"]), 1)

            # 验证列位置对象
            column_position = transaction["value"][0]
            self.assertEqual(column_position["columnPHID"], test_column_phid)
            self.assertEqual(
                column_position["beforePHIDs"],
                multiple_before,
                "应该支持多个 beforePHIDs",
            )
            self.assertEqual(
                column_position["afterPHIDs"], multiple_after, "应该支持多个 afterPHIDs"
            )

        with self.subTest("Type consistency across all variants"):
            """验证所有变体都返回相同的基本类型结构"""
            variants = [
                # 简单列事务
                self.cli.create_column_transaction(column_phid=test_column_phid),
                # 只包含 before
                self.cli.create_column_transaction(
                    column_phid=test_column_phid, before_phids=[test_before_phid]
                ),
                # 只包含 after
                self.cli.create_column_transaction(
                    column_phid=test_column_phid, after_phids=[test_after_phid]
                ),
                # 包含两者
                self.cli.create_column_transaction(
                    column_phid=test_column_phid,
                    before_phids=[test_before_phid],
                    after_phids=[test_after_phid],
                ),
            ]

            for i, transaction in enumerate(variants):
                with self.subTest(variant=i):
                    # 所有变体都应该有相同的基本类型结构
                    self.assertEqual(
                        transaction["type"], "column", f"变体 {i} 的类型应该是 'column'"
                    )
                    self.assertIsInstance(
                        transaction["value"], list, f"变体 {i} 的 value 必须是列表"
                    )
                    self.assertEqual(
                        len(transaction["value"]),
                        1,
                        f"变体 {i} 的列表应该只包含一个元素",
                    )
                    self.assertIsInstance(
                        transaction["value"][0], dict, f"变体 {i} 的列表元素应该是字典"
                    )
                    self.assertEqual(
                        transaction["value"][0]["columnPHID"],
                        test_column_phid,
                        f"变体 {i} 的 columnPHID 应该正确",
                    )

    def test_column_transaction_prevents_api_error(self):
        """
        测试修复后的列事务不会导致 "Expected a list" API 错误。

        这是一个回归测试，确保之前修复的问题不会重新出现。
        """
        test_column_phid = "PHID-PCOL-TESTCOLUMN"

        # 模拟用户原始调用场景
        transaction = self.cli.create_column_transaction(column_phid=test_column_phid)

        # 验证事务格式符合 Phabricator API 要求
        self.assertEqual(transaction["type"], "column")

        # 关键验证：value 必须是列表，这是导致原始错误的原因
        self.assertIsInstance(
            transaction["value"],
            list,
            "修复后的列事务必须返回列表格式以避免 'Expected a list' 错误",
        )

        # 验证列表内容
        self.assertGreater(len(transaction["value"]), 0, "列表不能为空")
        self.assertIsInstance(
            transaction["value"][0], dict, "列表元素必须是包含列位置信息的字典"
        )

        # 验证列位置信息结构
        column_position = transaction["value"][0]
        self.assertIn("columnPHID", column_position, "必须包含 columnPHID 字段")
        self.assertEqual(
            column_position["columnPHID"], test_column_phid, "columnPHID 值必须正确"
        )

        # 这个测试确保了修复的有效性，防止回归
        # 如果这里失败，说明 "Expected a list, but value is not a list" 错误可能会重新出现
