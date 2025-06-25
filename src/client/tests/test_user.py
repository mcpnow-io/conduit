from unittest import TestCase

from src.client.user import UserClient
from src.conduit import get_config


class TestManiphestClient(TestCase):
    def setUp(self):
        super().setUp()
        config = get_config()
        self.cli = UserClient(config.url, config.token)

    def test_whoami(self):
        self.cli.whoami()
