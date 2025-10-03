from typing import Any, Dict, List

from conduit.client.base import BasePhabricatorClient
from conduit.utils import build_search_params, build_transaction_params


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

    def create_column(
        self, project_phid: str, name: str, limit: int = None
    ) -> Dict[str, Any]:
        """
        Create a new workboard column in a project.

        Args:
            project_phid: PHID of the project to create column in
            name: Name of the column
            limit: Column limit (optional)

        Returns:
            Created column data
        """
        transactions = [
            {"type": "name", "value": name},
            {"type": "projectPHID", "value": project_phid},
        ]

        if limit is not None:
            transactions.append({"type": "limit", "value": str(limit)})

        params = build_transaction_params(transactions=transactions)
        return self._make_request("project.column.create", params)

    def edit_column(
        self, column_phid: str, transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Edit an existing workboard column.

        Args:
            column_phid: PHID of the column to edit
            transactions: List of transaction objects

        Returns:
            Updated column data
        """
        params = build_transaction_params(
            transactions=transactions, object_identifier=column_phid
        )
        return self._make_request("project.column.edit", params)

    def delete_column(self, column_phid: str) -> Dict[str, Any]:
        """
        Delete a workboard column.

        Args:
            column_phid: PHID of the column to delete

        Returns:
            Deletion result
        """
        params = {"objectIdentifier": column_phid}
        return self._make_request("project.column.delete", params)

    # Convenience methods for common column operations
    def update_column_name(self, column_phid: str, new_name: str) -> Dict[str, Any]:
        """
        Update the name of a workboard column.

        Args:
            column_phid: PHID of the column to update
            new_name: New name for the column

        Returns:
            Updated column data
        """
        transactions = [{"type": "name", "value": new_name}]
        return self.edit_column(column_phid, transactions)

    def update_column_limit(self, column_phid: str, limit: int) -> Dict[str, Any]:
        """
        Update the task limit of a workboard column.

        Args:
            column_phid: PHID of the column to update
            limit: New task limit for the column

        Returns:
            Updated column data
        """
        transactions = [{"type": "limit", "value": str(limit)}]
        return self.edit_column(column_phid, transactions)
