from unittest import TestCase

from src.client.types import UserInfo, UserSearchAttachments, UserSearchConstraints
from src.client.user import UserClient
from src.conduit import get_config


class TestUserClient(TestCase):
    def setUp(self):
        super().setUp()
        config = get_config()
        self.cli = UserClient(config.url, config.token)

        # Get current user info for reference
        self.user: UserInfo = self.cli.whoami()

    def test_whoami(self):
        """Test the existing whoami method"""
        user = self.cli.whoami()
        self.assertIn("phid", user)
        self.assertIn("userName", user)
        self.assertIn("realName", user)

    def test_search_basic(self):
        """Test basic user search without constraints"""
        results = self.cli.search(limit=5)

        self.assertIn("data", results)
        self.assertIn("cursor", results)
        self.assertIsInstance(results["data"], list)

        # Should have at least one user (current user)
        self.assertGreater(len(results["data"]), 0)

        # Check structure of first result
        if results["data"]:
            user = results["data"][0]
            self.assertIn("id", user)
            self.assertIn("phid", user)
            self.assertIn("fields", user)

            fields = user["fields"]
            self.assertIn("username", fields)

    def test_search_with_query_key(self):
        """Test search with builtin query key"""
        results = self.cli.search(query_key="active", limit=5)

        self.assertIn("data", results)
        self.assertIsInstance(results["data"], list)

    def test_search_with_constraints(self):
        """Test search with constraints"""
        # Search by username
        constraints: UserSearchConstraints = {"usernames": [self.user["userName"]]}
        results = self.cli.search(constraints=constraints)

        self.assertIn("data", results)
        self.assertEqual(len(results["data"]), 1)

        found_user = results["data"][0]
        self.assertEqual(found_user["fields"]["username"], self.user["userName"])

    def test_search_admin_constraint(self):
        """Test search with admin constraint"""
        constraints: UserSearchConstraints = {"isAdmin": True}
        results = self.cli.search(constraints=constraints)

        self.assertIn("data", results)
        # Should find at least one admin user
        self.assertGreater(len(results["data"]), 0)

        # Check that found users have admin role
        for user in results["data"]:
            roles = user["fields"].get("roles", [])
            self.assertIn("admin", roles)

    def test_search_with_attachments(self):
        """Test search with attachments"""
        attachments: UserSearchAttachments = {"availability": True}
        results = self.cli.search(
            constraints={"usernames": [self.user["userName"]]}, attachments=attachments
        )

        self.assertIn("data", results)
        self.assertEqual(len(results["data"]), 1)

        user = results["data"][0]
        if "attachments" in user:
            self.assertIn("availability", user["attachments"])

    def test_search_with_ordering(self):
        """Test search with different orderings"""
        # Test with newest ordering
        results = self.cli.search(order="newest", limit=3)
        self.assertIn("data", results)

        # Test with oldest ordering
        results = self.cli.search(order="oldest", limit=3)
        self.assertIn("data", results)

    def test_search_pagination(self):
        """Test search pagination"""
        # Get first page
        first_page = self.cli.search(limit=1)

        self.assertIn("data", first_page)
        self.assertIn("cursor", first_page)

        # If there's more than one user, test pagination
        if first_page["cursor"].get("after"):
            second_page = self.cli.search(after=first_page["cursor"]["after"], limit=1)

            self.assertIn("data", second_page)

            # Results should be different
            if first_page["data"] and second_page["data"]:
                self.assertNotEqual(
                    first_page["data"][0]["id"], second_page["data"][0]["id"]
                )

    def test_search_name_like(self):
        """Test search with nameLike constraint"""
        constraints: UserSearchConstraints = {"nameLike": "admin"}
        results = self.cli.search(constraints=constraints)

        self.assertIn("data", results)

        # Check that all results contain "admin" in username or real name
        for user in results["data"]:
            username = user["fields"].get("username", "").lower()
            real_name = user["fields"].get("realName", "").lower()
            self.assertTrue(
                "admin" in username or "admin" in real_name,
                f"User {username} ({real_name}) does not contain 'admin'",
            )

    def test_search_empty_result(self):
        """Test search that should return no results"""
        constraints: UserSearchConstraints = {"usernames": ["nonexistent_user_12345"]}
        results = self.cli.search(constraints=constraints)

        self.assertIn("data", results)
        self.assertEqual(len(results["data"]), 0)
