"""
Maniphest (Task Management) API client.
"""

from typing import Any, Dict, List

from .base import BaseAsyncPhabricatorClient, BasePhabricatorClient, PhabricatorAPIError


class ManiphestClient(BasePhabricatorClient):
    """
    Client for Maniphest (Task Management) API operations.

    Handles task creation, search, updates, and other task-related operations.
    """

    def search_tasks(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search for Maniphest tasks.

        Args:
            constraints: Search constraints (e.g., {'statuses': ['open']})
            limit: Maximum number of results to return

        Returns:
            Search results with task data
        """
        params = {"limit": limit}

        if constraints:
            params["constraints"] = constraints

        return self._make_request("maniphest.search", params)

    def get_task(self, task_id: int) -> Dict[str, Any]:
        """
        Get a specific task by ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            Task data
        """
        constraints = {"ids": [task_id]}
        result = self.search_tasks(constraints=constraints, limit=1)

        if result.get("data"):
            return result["data"][0]
        else:
            raise PhabricatorAPIError(f"Task {task_id} not found")

    def create_task(
        self,
        title: str,
        description: str = "",
        owner_phid: str = None,
        project_phids: List[str] = None,
        priority: str = None,
    ) -> Dict[str, Any]:
        """
        Create a new Maniphest task.

        Args:
            title: Task title
            description: Task description
            owner_phid: PHID of the task owner
            project_phids: List of project PHIDs to associate with the task
            priority: Task priority ('unbreak', 'high', 'normal', 'low', 'wish')

        Returns:
            Created task data
        """
        transactions = [{"type": "title", "value": title}]

        if description:
            transactions.append({"type": "description", "value": description})

        if owner_phid:
            transactions.append({"type": "owner", "value": owner_phid})

        if project_phids:
            transactions.append({"type": "projects.set", "value": project_phids})

        if priority:
            transactions.append({"type": "priority", "value": priority})

        params = {"transactions": transactions}

        return self._make_request("maniphest.edit", params)

    def update_task(
        self, task_id: int, transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update an existing task.

        Args:
            task_id: ID of the task to update
            transactions: List of transaction objects

        Returns:
            Updated task data
        """
        params = {"objectIdentifier": task_id, "transactions": transactions}

        return self._make_request("maniphest.edit", params)

    def get_task_transactions(self, task_id: int) -> Dict[str, Any]:
        """
        Get transaction history for a task.

        Args:
            task_id: Task ID

        Returns:
            Transaction history
        """
        return self._make_request("maniphest.gettasktransactions", {"ids": [task_id]})

    def query_tasks(self, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute complex searches for Maniphest tasks (legacy method).

        Args:
            constraints: Query constraints

        Returns:
            Query results
        """
        params = constraints or {}
        return self._make_request("maniphest.query", params)

    def get_task_info(self, task_id: int) -> Dict[str, Any]:
        """
        Retrieve information about a Maniphest task (legacy method).

        Args:
            task_id: Task ID

        Returns:
            Task information
        """
        return self._make_request("maniphest.info", {"task_id": task_id})

    def get_priority_info(self) -> Dict[str, Any]:
        """
        Read information about task priorities.

        Returns:
            Priority information
        """
        return self._make_request("maniphest.priority.search")

    def get_status_info(self) -> Dict[str, Any]:
        """
        Read information about task statuses.

        Returns:
            Status information
        """
        return self._make_request("maniphest.status.search")

    def query_statuses(self) -> Dict[str, Any]:
        """
        Retrieve information about possible Maniphest task status values (legacy).

        Returns:
            Status values
        """
        return self._make_request("maniphest.querystatuses")


class AsyncManiphestClient(BaseAsyncPhabricatorClient):
    """
    Async client for Maniphest (Task Management) API operations.
    """

    async def search_tasks(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """Search for tasks asynchronously."""
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints
        return await self._make_request("maniphest.search", params)

    async def get_task(self, task_id: int) -> Dict[str, Any]:
        """Get a specific task by ID asynchronously."""
        constraints = {"ids": [task_id]}
        result = await self.search_tasks(constraints=constraints, limit=1)

        if result.get("data"):
            return result["data"][0]
        else:
            raise PhabricatorAPIError(f"Task {task_id} not found")

    async def create_task(
        self,
        title: str,
        description: str = "",
        owner_phid: str = None,
        project_phids: List[str] = None,
        priority: str = None,
    ) -> Dict[str, Any]:
        """Create a task asynchronously."""
        transactions = [{"type": "title", "value": title}]

        if description:
            transactions.append({"type": "description", "value": description})
        if owner_phid:
            transactions.append({"type": "owner", "value": owner_phid})
        if project_phids:
            transactions.append({"type": "projects.set", "value": project_phids})
        if priority:
            transactions.append({"type": "priority", "value": priority})

        params = {"transactions": transactions}
        return await self._make_request("maniphest.edit", params)

    async def update_task(
        self, task_id: int, transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update an existing task asynchronously."""
        params = {"objectIdentifier": task_id, "transactions": transactions}
        return await self._make_request("maniphest.edit", params)
