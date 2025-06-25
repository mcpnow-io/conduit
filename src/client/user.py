from typing import Any, Dict, List

from src.client.types import UserInfo

from .base import BaseAsyncPhabricatorClient, BasePhabricatorClient


class UserClient(BasePhabricatorClient):
    def search_users(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search for users.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Search results with user data
        """
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints

        return self._make_request("user.search", params)

    def edit_user(
        self, transactions: List[Dict[str, Any]], object_identifier: str
    ) -> Dict[str, Any]:
        """
        Apply transactions to edit a user. (Users cannot be created via the API.)

        Args:
            transactions: List of transaction objects
            object_identifier: User identifier to update

        Returns:
            User data
        """
        params = {"transactions": transactions, "objectIdentifier": object_identifier}

        return self._make_request("user.edit", params)

    def whoami(self) -> UserInfo:
        """
        Retrieve information about the logged-in user.

        Returns:
            Current user information
        """
        return self._make_request("user.whoami")

    def query_users(self, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Query users (legacy method).

        Args:
            constraints: Query constraints

        Returns:
            Query results
        """
        params = constraints or {}
        return self._make_request("user.query", params)

    def test_connection(self) -> Dict[str, Any]:
        """
        Test the API connection by calling user.whoami.

        Returns:
            User information if successful
        """
        return self.whoami()


class AsyncUserClient(BaseAsyncPhabricatorClient):
    """
    Async client for User management API operations.
    """

    async def search_users(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """Search for users asynchronously."""
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints
        return await self._make_request("user.search", params)

    async def whoami(self) -> Dict[str, Any]:
        """Get current user information asynchronously."""
        return await self._make_request("user.whoami")

    async def test_connection(self) -> Dict[str, Any]:
        """Test the API connection asynchronously."""
        return await self.whoami()
