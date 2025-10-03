from typing import List, Optional, Union

from conduit.client.types import (
    UserInfo,
    UserSearchAttachments,
    UserSearchConstraints,
    UserSearchResults,
)
from conduit.client.base import BasePhabricatorClient

from conduit.utils import build_search_params


class UserClient(BasePhabricatorClient):
    def whoami(self) -> UserInfo:
        """
        Retrieve information about the logged-in user.

        Returns:
            Current user information
        """
        return self._make_request("user.whoami")

    def search(
        self,
        query_key: Optional[str] = None,
        constraints: Optional[UserSearchConstraints] = None,
        attachments: Optional[UserSearchAttachments] = None,
        order: Optional[Union[str, List[str]]] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: int = 100,
    ) -> UserSearchResults:
        """
        Search for users using the modern search API.

        Args:
            query_key: Builtin query key ("active", "admin", "all", "approval")
            constraints: Search constraints (e.g., {'usernames': ['admin']})
            attachments: Additional data to include in results
            order: Result ordering (builtin key or list of columns)
            before: Cursor for previous page
            after: Cursor for next page
            limit: Maximum number of results to return (default: 100)

        Returns:
            Search results with user data, cursor info, and attachments
        """
        params = build_search_params(
            query_key=query_key,
            constraints=constraints,
            attachments=attachments,
            order=order,
            before=before,
            after=after,
            limit=limit,
        )
        return self._make_request("user.search", params)
