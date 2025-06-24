from unittest import TestCase

from src.client.base import PhabricatorAPIError
from src.client.maniphest import ManiphestClient
from src.client.types import ManiphestTaskInfo
from src.conduit import get_config


class TestManiphestClient(TestCase):
    def setUp(self):
        super().setUp()
        config = get_config()
        self.cli = ManiphestClient(config.url, config.token)

        self.task: ManiphestTaskInfo = self.cli.create_task("Test")

    def test_get_task(self):
        with self.subTest("Get existing task"):
            self.cli.get_task(self.task["id"])

        with self.subTest("Get non-existing Task"):
            with self.assertRaises(PhabricatorAPIError):
                self.cli.get_task(0)
