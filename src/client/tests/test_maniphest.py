from unittest import TestCase

from src.client.base import PhabricatorAPIError
from src.client.maniphest import ManiphestClient
from src.client.types import (
    ManiphestTaskInfo,
    ManiphestTaskTransactionParentsAdd,
    ManiphestTaskTransactionParentsRemove,
    ManiphestTaskTransactionParentsSet,
    ManiphestTaskTransactionSubtasksAdd,
    ManiphestTaskTransactionSubtasksRemove,
    ManiphestTaskTransactionSubtasksSet,
)
from src.conduit import get_config


class TestManiphestClient(TestCase):
    def setUp(self):
        super().setUp()
        config = get_config()
        self.cli = ManiphestClient(config.url, config.token)

        self.task: ManiphestTaskInfo = self.cli.create_task("Test")
        self.task2: ManiphestTaskInfo = self.cli.create_task("Test2")

    def test_get_task(self):
        with self.subTest("Get existing task"):
            self.cli.get_task(self.task["id"])

        with self.subTest("Get non-existing Task"):
            with self.assertRaises(PhabricatorAPIError):
                self.cli.get_task(0)

    def test_edit_task_subtask(self):
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
