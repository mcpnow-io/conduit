from typing import Any, Dict, List

from src.client.base import BasePhabricatorClient
from src.utils import build_search_params, build_transaction_params


class ProjectClient(BasePhabricatorClient):
    def search_projects(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search for projects.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Search results with project data
        """
        params = build_search_params(
            constraints=constraints,
            limit=limit,
        )
        return self._make_request("project.search", params)

    def edit_project(
        self, transactions: List[Dict[str, Any]], object_identifier: str = None
    ) -> Dict[str, Any]:
        """
        Apply transactions to create a new project or edit an existing one.

        Args:
            transactions: List of transaction objects
            object_identifier: Existing project identifier to update

        Returns:
            Project data
        """
        params = build_transaction_params(
            transactions=transactions,
            object_identifier=object_identifier,
        )
        return self._make_request("project.edit", params)

    def create_project(
        self, name: str, description: str = "", icon: str = None, color: str = None
    ) -> Dict[str, Any]:
        """
        Create a new project.

        Args:
            name: Project name
            description: Project description
            icon: Project icon
            color: Project color

        Returns:
            Created project data
        """
        transactions = [{"type": "name", "value": name}]

        if description:
            transactions.append({"type": "description", "value": description})
        if icon:
            transactions.append({"type": "icon", "value": icon})
        if color:
            transactions.append({"type": "color", "value": color})

        return self.edit_project(transactions)

    def search_columns(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Read information about workboard columns.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Column information
        """
        params = build_search_params(
            constraints=constraints,
            limit=limit,
        )
        return self._make_request("project.column.search", params)

    def query_projects(self, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute searches for Projects (legacy method).

        Args:
            constraints: Query constraints

        Returns:
            Query results
        """
        params = constraints or {}
        return self._make_request("project.query", params)
