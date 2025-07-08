import os
import unittest
from unittest.mock import MagicMock, patch

from src.conduit import PhabricatorConfig, get_client


class TestUserAgentFilter(unittest.TestCase):
    def setUp(self):
        self.original_env = os.environ.copy()
        os.environ["PHABRICATOR_URL"] = "https://test.example.com"
        os.environ.pop("PHABRICATOR_TOKEN", None)
        os.environ.pop("CONDUIT_USER_AGENT_FILTER", None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)
        # Reset global config
        import src.conduit

        src.conduit.config = None
        src.conduit.client = None

    def test_config_loads_user_agent_filter(self):

        with self.subTest("Without filter"):
            config = PhabricatorConfig(require_token=False)
            self.assertIsNone(config.user_agent_filter)

        with self.subTest("With filter"):
            os.environ["CONDUIT_USER_AGENT_FILTER"] = "test-agent"
            config = PhabricatorConfig(require_token=False)
            self.assertEqual(config.user_agent_filter, "test-agent")

    @patch("src.conduit.get_http_headers")
    def test_sse_mode_access_control(self, mock_headers):
        os.environ["CONDUIT_USER_AGENT_FILTER"] = "approved-client"

        import src.conduit

        src.conduit.use_sse = True

        mock_headers.return_value = {
            "user-agent": "approved-client/1.0",
            "x-phabricator-token": "12345678901234567890123456789012",
        }

        with patch("src.conduit.PhabricatorClient") as mock_client:
            mock_client.return_value = MagicMock()
            client = get_client()
            self.assertIsNotNone(client)

        mock_headers.return_value = {
            "user-agent": "malicious-client/1.0",
            "x-phabricator-token": "12345678901234567890123456789012",
        }

        with self.assertRaises(ValueError) as context:
            get_client()

        self.assertIn("Access denied", str(context.exception))

    @patch("src.conduit.get_http_headers")
    def test_stdio_mode_ignores_filter(self, mock_headers):
        os.environ["PHABRICATOR_TOKEN"] = "12345678901234567890123456789012"

        mock_headers.return_value = {"user-agent": "malicious-client/1.0"}

        import src.conduit

        src.conduit.use_sse = False

        with patch("src.conduit.PhabricatorClient") as mock_client:
            mock_client.return_value = MagicMock()
            client = get_client()
            self.assertIsNotNone(client)


if __name__ == "__main__":
    unittest.main()
