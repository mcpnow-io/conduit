import json
from typing import Any, Dict, List, Optional, Union

from .base import BasePhabricatorClient
from .types import PHID, ManiphestTaskInfo, PolicyID


class ManiphestClient(BasePhabricatorClient):
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

    def get_task(self, task_id: int) -> ManiphestTaskInfo:
        """
        Get a specific task by ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            Task data
        """
        params = {"task_id": task_id}

        return self._make_request("maniphest.info", params)

    def create_task(
        self,
        title: str,
        description: Optional[str] = "",
        owner_phid: Optional[str] = None,
        view_policy: Optional[Union[PHID, PolicyID]] = None,
        edit_policy: Optional[Union[PHID, PolicyID]] = None,
        cc_phids: Optional[List[PHID]] = None,
        priority: Optional[int] = None,
        project_phids: Optional[List[PHID]] = None,
        auxiliary: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new Maniphest task.

        Args:
            title: Task title
            description: Task description in Phabricator Markdown format
            owner_phid: PHID of the task owner
            viewPolicy: optional phid or policy string
            editPolicy: optional phid or policy string
            cc_phids: List of PHIDs to add as CCs
            priority: Task priority (0/25/50/80/90/100, where 100 is highest)
            project_phids: List of PHIDs for projects to associate with the task
            auxiliary: Additional auxiliary data to include in the task

        Returns:
            Created task data
        """
        params = {"title": title}

        if description:
            params["description"] = description

        if owner_phid:
            params["ownerPHID"] = owner_phid

        if view_policy:
            params["viewPolicy"] = view_policy

        if edit_policy:
            params["editPolicy"] = edit_policy

        if cc_phids:
            params["ccPHIDs"] = json.dumps(cc_phids)

        if priority:
            params["priority"] = priority

        if project_phids:
            params["projectPHIDs"] = json.dumps(project_phids)

        if auxiliary:
            params["auxiliary"] = json.dumps(auxiliary)

        return self._make_request("maniphest.createtask", params)

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
