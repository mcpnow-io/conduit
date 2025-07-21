from typing import List, Optional, Union

from src.client.types import (
    UserInfo,
    UserSearchAttachments,
    UserSearchConstraints,
    UserSearchResults,
)

from .base import BasePhabricatorClient


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
        params = {"limit": limit}

        if query_key:
            params["queryKey"] = query_key

        if constraints:
            # Use flatten_params like maniphest does
            flattened_constraints = dict(
                self.flatten_params(constraints, "constraints")
            )
            params.update(flattened_constraints)

        if attachments:
            # Use flatten_params for attachments too
            flattened_attachments = dict(
                self.flatten_params(attachments, "attachments")
            )
            params.update(flattened_attachments)

        if order:
            params["order"] = order

        if before:
            params["before"] = before

        if after:
            params["after"] = after

        return self._make_request("user.search", params)
