import os
from unittest import TestCase
from unittest.mock import patch

from conduit.conduit import ConduitApp, PhabricatorConfig


class TestSSEModeSecurity(TestCase):
    """Test SSE mode security and user identity isolation."""

    def setUp(self):
        super().setUp()
        # Set up test environment variables
        os.environ["PHABRICATOR_URL"] = "https://test.example.com/api/"

        # Create test configuration
        self.config = PhabricatorConfig(require_token=False)
        self.app = ConduitApp(self.config, use_sse=True)

    def tearDown(self):
        super().tearDown()
        # Clean up environment variables
        if "PHABRICATOR_URL" in os.environ:
            del os.environ["PHABRICATOR_URL"]

    @patch("conduit.conduit.get_http_headers")
    def test_sse_mode_prevents_client_caching(self, mock_get_headers):
        """Test that SSE mode prevents client caching and ensures user identity isolation."""
        # Simulate first user request
        token_a = "user_a_token_" + "x" * 19  # 32-character token
        mock_get_headers.return_value = {"x-phabricator-token": token_a}

        client_a = self.app.get_client()
        self.assertIsNotNone(client_a)

        # Simulate second user request
        token_b = "user_b_token_" + "y" * 19  # 32-character token
        mock_get_headers.return_value = {"x-phabricator-token": token_b}

        client_b = self.app.get_client()
        self.assertIsNotNone(client_b)

        # Verify that two clients are different instances
        self.assertNotEqual(id(client_a), id(client_b))

        # Verify that clients use different tokens
        self.assertNotEqual(client_a.maniphest.api_token, client_b.maniphest.api_token)
        self.assertEqual(client_a.maniphest.api_token, token_a)
        self.assertEqual(client_b.maniphest.api_token, token_b)

        # Verify that client instances are completely independent
        self.assertNotEqual(client_a, client_b)

    @patch("conduit.conduit.get_http_headers")
    def test_sse_mode_multiple_user_isolation(self, mock_get_headers):
        """Test complete isolation of multiple users in SSE mode."""
        tokens = [
            f"user{i}_token_{'x' * 20}"
            for i in range(5)  # 5 different 32-character tokens
        ]
        clients = []

        # Simulate requests from 5 different users
        for i, token in enumerate(tokens):
            mock_get_headers.return_value = {"x-phabricator-token": token}
            client = self.app.get_client()
            clients.append(client)

            # Verify that each client uses the correct token
            self.assertEqual(client.user.api_token, token)

        # Verify that all clients are independent instances
        for i in range(len(clients)):
            for j in range(i + 1, len(clients)):
                self.assertNotEqual(clients[i], clients[j])
                self.assertNotEqual(
                    clients[i].user.api_token, clients[j].user.api_token
                )

    @patch("conduit.conduit.get_http_headers")
    def test_sse_mode_token_validation(self, mock_get_headers):
        """Test token validation in SSE mode."""
        # Test missing token
        mock_get_headers.return_value = {}

        with self.assertRaises(ValueError) as cm:
            self.app.get_client()

        self.assertIn("Must provide X-PHABRICATOR-TOKEN", str(cm.exception))

        # Test incorrect token length
        mock_get_headers.return_value = {"x-phabricator-token": "short_token"}

        with self.assertRaises(ValueError) as cm:
            self.app.get_client()

        self.assertIn("must be exactly 32 characters", str(cm.exception))

        # Test correct token length
        valid_token = "valid_token_" + "x" * 20  # 32-character token
        mock_get_headers.return_value = {"x-phabricator-token": valid_token}

        client = self.app.get_client()
        self.assertIsNotNone(client)
        self.assertEqual(client.maniphest.api_token, valid_token)

    @patch("conduit.conduit.get_http_headers")
    def test_sse_mode_no_persistent_state(self, mock_get_headers):
        """Test that SSE mode has no persistent state pollution."""
        # First user
        token_1 = "first_user_token_" + "x" * 15  # 32-character token
        mock_get_headers.return_value = {"x-phabricator-token": token_1}

        client_1 = self.app.get_client()
        self.assertIsNotNone(client_1)
        self.assertEqual(client_1.maniphest.api_token, token_1)

        # Second user
        token_2 = "second_user_token" + "y" * 15  # 32-character token
        mock_get_headers.return_value = {"x-phabricator-token": token_2}

        client_2 = self.app.get_client()
        self.assertIsNotNone(client_2)
        self.assertEqual(client_2.maniphest.api_token, token_2)

        # Third user
        token_3 = "third_user_token_" + "z" * 15  # 32-character token
        mock_get_headers.return_value = {"x-phabricator-token": token_3}

        client_3 = self.app.get_client()
        self.assertIsNotNone(client_3)
        self.assertEqual(client_3.maniphest.api_token, token_3)

        # Verify no state pollution
        self.assertEqual(client_1.user.api_token, token_1)
        self.assertEqual(client_2.user.api_token, token_2)
        self.assertEqual(client_3.user.api_token, token_3)

        # Verify that all clients are independent
        self.assertNotEqual(client_1, client_2)
        self.assertNotEqual(client_2, client_3)
        self.assertNotEqual(client_1, client_3)

    def test_stdio_mode_backward_compatibility(self):
        """Test that stdio mode maintains backward compatibility (still caches clients)."""
        # Create stdio mode application
        stdio_config = PhabricatorConfig(
            token="stdio_test_token" + "x" * 16, require_token=False
        )
        stdio_app = ConduitApp(stdio_config, use_sse=False)

        # First call
        client_1 = stdio_app.get_client()
        self.assertIsNotNone(client_1)
        self.assertEqual(client_1.user.api_token, "stdio_test_token" + "x" * 16)

        # Second call should return the same client instance
        client_2 = stdio_app.get_client()
        self.assertIs(client_1, client_2)
        self.assertEqual(client_2.user.api_token, "stdio_test_token" + "x" * 16)

    @patch("conduit.conduit.get_http_headers")
    def test_sse_mode_concurrent_requests_simulation(self, mock_get_headers):
        """Simulate concurrent request scenarios in SSE mode."""
        # Simulate rapid consecutive requests to simulate concurrent scenarios
        tokens = [
            f"concurrent_{i:02d}_" + "x" * (32 - len(f"concurrent_{i:02d}_"))
            for i in range(10)
        ]
        clients = []

        # Rapidly create clients to simulate concurrent requests
        for token in tokens:
            mock_get_headers.return_value = {"x-phabricator-token": token}
            client = self.app.get_client()
            clients.append(client)

        # Verify that each client uses the correct token
        for i, client in enumerate(clients):
            self.assertEqual(client.user.api_token, tokens[i])

        # Verify that all clients are independent
        for i in range(len(clients)):
            for j in range(i + 1, len(clients)):
                self.assertNotEqual(clients[i], clients[j])

    @patch("conduit.conduit.get_http_headers")
    def test_sse_mode_security_boundary(self, mock_get_headers):
        """Test security boundaries in SSE mode."""
        # Simulate malicious user attempting to access other users' data
        admin_token = "admin_secure_token" + "x" * 14  # 32-character token
        user_token = "regular_user_token" + "y" * 14  # 32-character token

        # Admin request
        mock_get_headers.return_value = {"x-phabricator-token": admin_token}
        admin_client = self.app.get_client()
        self.assertEqual(admin_client.user.api_token, admin_token)

        # Regular user request
        mock_get_headers.return_value = {"x-phabricator-token": user_token}
        user_client = self.app.get_client()
        self.assertEqual(user_client.user.api_token, user_token)

        # Verify security boundary: regular user client cannot access admin token
        self.assertNotEqual(admin_client.user.api_token, user_client.user.api_token)
        self.assertNotEqual(admin_client, user_client)

        # Another admin request should create a new client instead of reusing
        mock_get_headers.return_value = {"x-phabricator-token": admin_token}
        admin_client_2 = self.app.get_client()
        self.assertEqual(admin_client_2.user.api_token, admin_token)

        # Verify that it's a new client instance
        self.assertNotEqual(admin_client, admin_client_2)
        self.assertEqual(admin_client_2.user.api_token, admin_token)


class TestSSEModeSecurityIntegration(TestCase):
    """Integration tests for SSE mode security."""

    def setUp(self):
        super().setUp()
        os.environ["PHABRICATOR_URL"] = "https://integration.test.com/api/"

    def tearDown(self):
        super().tearDown()
        if "PHABRICATOR_URL" in os.environ:
            del os.environ["PHABRICATOR_URL"]

    @patch("conduit.conduit.get_http_headers")
    def test_integration_with_real_phabricator_client(self, mock_get_headers):
        """Test integration with real PhabricatorClient."""
        from conduit.client.unified import PhabricatorClient

        config = PhabricatorConfig(require_token=False)
        app = ConduitApp(config, use_sse=True)

        # Simulate real user token
        real_token = "phabricator_api_" + "x" * 16  # 32-character token
        mock_get_headers.return_value = {"x-phabricator-token": real_token}

        client = app.get_client()

        # Verify that the correct PhabricatorClient instance is returned
        self.assertIsInstance(client, PhabricatorClient)
        self.assertEqual(client.user.api_token, real_token)

        # Verify that client configuration is correct
        self.assertEqual(client.user.api_url, "https://integration.test.com/api/")

    def test_app_mode_configuration(self):
        """Test correctness of application mode configuration."""
        # Test SSE mode configuration
        sse_config = PhabricatorConfig(require_token=False)
        sse_app = ConduitApp(sse_config, use_sse=True)
        self.assertTrue(sse_app.use_sse)

        # Test stdio mode configuration
        stdio_config = PhabricatorConfig(
            token="test_token_xx" + "x" * 19, require_token=False
        )
        stdio_app = ConduitApp(stdio_config, use_sse=False)
        self.assertFalse(stdio_app.use_sse)
