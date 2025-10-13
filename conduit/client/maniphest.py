from typing import Any, Dict, List, Optional, Union

from conduit.client.base import BasePhabricatorClient
from conduit.client.types import (
    PHID,
    ManiphestSearchAttachments,
    ManiphestSearchConstraints,
    ManiphestSearchResults,
    ManiphestTaskInfo,
    ManiphestTaskTransaction,
    PolicyID,
)
from conduit.utils import (
    build_search_params,
    build_transaction_params,
    serialize_json_params,
)


class ManiphestClient(BasePhabricatorClient):
    def search_tasks(
        self,
        query_key: Optional[str] = None,
        constraints: Optional[ManiphestSearchConstraints] = None,
        attachments: Optional[ManiphestSearchAttachments] = None,
        order: Optional[Union[str, List[str]]] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: int = 100,
    ) -> ManiphestSearchResults:
        """
        Search for Maniphest tasks using the modern search API.

        Args:
            query_key: Builtin query key ("assigned", "authored", "subscribed", "open", "all")
            constraints: Search constraints (e.g., {'statuses': ['open']})
            attachments: Additional data to include in results
            order: Result ordering (builtin key or list of columns)
            before: Cursor for previous page
            after: Cursor for next page
            limit: Maximum number of results to return (default: 100)

        Returns:
            Search results with task data, cursor info, and attachments
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
            params["ccPHIDs"] = cc_phids

        if priority:
            params["priority"] = priority

        if project_phids:
            params["projectPHIDs"] = project_phids

        if auxiliary:
            params["auxiliary"] = auxiliary

        # Serialize list and dict fields to JSON
        params = serialize_json_params(params)

        return self._make_request("maniphest.createtask", params)

    def edit_task(
        self,
        object_identifier: Optional[Union[int, PHID, str]] = None,
        transactions: Optional[List[ManiphestTaskTransaction]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new task or edit an existing one using the maniphest.edit endpoint.

        Args:
            object_identifier: Optional task ID, PHID, or object name to edit.
                             If None, creates a new task.
            transactions: List of transaction objects to apply

        Returns:
            Task data (created or updated)
        """
        params = {}

        if object_identifier is not None:
            params["objectIdentifier"] = object_identifier

        if transactions:
            params = build_transaction_params(
                transactions=transactions,
                object_identifier=object_identifier,
            )

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

    # Convenience methods for creating common transaction types
    @staticmethod
    def create_title_transaction(title: str) -> ManiphestTaskTransaction:
        """Create a transaction to update task title."""
        return {"type": "title", "value": title}

    @staticmethod
    def create_description_transaction(description: str) -> ManiphestTaskTransaction:
        """Create a transaction to update task description."""
        return {"type": "description", "value": description}

    @staticmethod
    def create_owner_transaction(
        owner_phid: Optional[PHID],
    ) -> ManiphestTaskTransaction:
        """Create a transaction to update task owner."""
        return {"type": "owner", "value": owner_phid}

    @staticmethod
    def create_status_transaction(status: str) -> ManiphestTaskTransaction:
        """Create a transaction to update task status."""
        return {"type": "status", "value": status}

    @staticmethod
    def create_priority_transaction(priority: str) -> ManiphestTaskTransaction:
        """Create a transaction to update task priority."""
        return {"type": "priority", "value": priority}

    @staticmethod
    def create_comment_transaction(comment: str) -> ManiphestTaskTransaction:
        """Create a transaction to add a comment."""
        return {"type": "comment", "value": comment}

    @staticmethod
    def create_projects_add_transaction(
        project_phids: List[PHID],
    ) -> ManiphestTaskTransaction:
        """Create a transaction to add project tags."""
        return {"type": "projects.add", "value": project_phids}

    @staticmethod
    def create_projects_remove_transaction(
        project_phids: List[PHID],
    ) -> ManiphestTaskTransaction:
        """Create a transaction to remove project tags."""
        return {"type": "projects.remove", "value": project_phids}

    @staticmethod
    def create_projects_set_transaction(
        project_phids: List[PHID],
    ) -> ManiphestTaskTransaction:
        """Create a transaction to set project tags (overwriting current)."""
        return {"type": "projects.set", "value": project_phids}

    @staticmethod
    def create_subscribers_add_transaction(
        user_phids: List[PHID],
    ) -> ManiphestTaskTransaction:
        """Create a transaction to add subscribers."""
        return {"type": "subscribers.add", "value": user_phids}

    @staticmethod
    def create_subscribers_remove_transaction(
        user_phids: List[PHID],
    ) -> ManiphestTaskTransaction:
        """Create a transaction to remove subscribers."""
        return {"type": "subscribers.remove", "value": user_phids}

    @staticmethod
    def create_subscribers_set_transaction(
        user_phids: List[PHID],
    ) -> ManiphestTaskTransaction:
        """Create a transaction to set subscribers (overwriting current)."""
        return {"type": "subscribers.set", "value": user_phids}

    @staticmethod
    def create_parent_transaction(parent_phid: PHID) -> ManiphestTaskTransaction:
        """Create a transaction to set task as subtask of another task."""
        return {"type": "parent", "value": parent_phid}

    @staticmethod
    def create_parents_add_transaction(
        parent_phids: List[PHID],
    ) -> ManiphestTaskTransaction:
        """Create a transaction to add parent tasks."""
        return {"type": "parents.add", "value": parent_phids}

    @staticmethod
    def create_parents_remove_transaction(
        parent_phids: List[PHID],
    ) -> ManiphestTaskTransaction:
        """Create a transaction to remove parent tasks."""
        return {"type": "parents.remove", "value": parent_phids}

    @staticmethod
    def create_parents_set_transaction(
        parent_phids: List[PHID],
    ) -> ManiphestTaskTransaction:
        """Create a transaction to set parent tasks (overwriting current)."""
        return {"type": "parents.set", "value": parent_phids}

    @staticmethod
    def create_subtasks_add_transaction(
        subtask_phids: List[PHID],
    ) -> ManiphestTaskTransaction:
        """Create a transaction to add subtasks."""
        return {"type": "subtasks.add", "value": subtask_phids}

    @staticmethod
    def create_subtasks_remove_transaction(
        subtask_phids: List[PHID],
    ) -> ManiphestTaskTransaction:
        """Create a transaction to remove subtasks."""
        return {"type": "subtasks.remove", "value": subtask_phids}

    @staticmethod
    def create_subtasks_set_transaction(
        subtask_phids: List[PHID],
    ) -> ManiphestTaskTransaction:
        """Create a transaction to set subtasks (overwriting current)."""
        return {"type": "subtasks.set", "value": subtask_phids}

    @staticmethod
    def create_column_transaction(
        column_phid: PHID,
        before_phid: Optional[PHID] = None,
        after_phid: Optional[PHID] = None,
    ) -> ManiphestTaskTransaction:
        """
        Create a transaction to move task to a workboard column.

        The Phabricator API expects a list of column PHIDs for simple moves. When
        positioning hints are provided, it accepts a list containing a single map
        with optional `beforePHID`/`afterPHID` keys.
        """
        if not before_phid and not after_phid:
            return {"type": "column", "value": [column_phid]}

        column_position: Dict[str, PHID] = {"columnPHID": column_phid}

        if before_phid:
            column_position["beforePHID"] = before_phid
        if after_phid:
            column_position["afterPHID"] = after_phid

        return {"type": "column", "value": [column_position]}

    @staticmethod
    def create_space_transaction(space_phid: PHID) -> ManiphestTaskTransaction:
        """Create a transaction to move task to a different space."""
        return {"type": "space", "value": space_phid}

    @staticmethod
    def create_view_policy_transaction(policy: str) -> ManiphestTaskTransaction:
        """Create a transaction to change view policy."""
        return {"type": "view", "value": policy}

    @staticmethod
    def create_edit_policy_transaction(policy: str) -> ManiphestTaskTransaction:
        """Create a transaction to change edit policy."""
        return {"type": "edit", "value": policy}

    @staticmethod
    def create_subtype_transaction(subtype: str) -> ManiphestTaskTransaction:
        """Create a transaction to change object subtype."""
        return {"type": "subtype", "value": subtype}

    @staticmethod
    def create_mfa_transaction(require_mfa: bool = True) -> ManiphestTaskTransaction:
        """Create a transaction to require MFA for this transaction group."""
        return {"type": "mfa", "value": require_mfa}

    # Helper methods for common search operations
    def search_open_tasks(
        self, attachments: Optional[ManiphestSearchAttachments] = None, limit: int = 100
    ) -> ManiphestSearchResults:
        """
        Search for open tasks using builtin query.

        Args:
            attachments: Additional data to include in results
            limit: Maximum number of results to return

        Returns:
            Search results with open tasks
        """
        return self.search_tasks(query_key="open", attachments=attachments, limit=limit)

    def search_assigned_tasks(
        self, attachments: Optional[ManiphestSearchAttachments] = None, limit: int = 100
    ) -> ManiphestSearchResults:
        """
        Search for tasks assigned to the current user.

        Args:
            attachments: Additional data to include in results
            limit: Maximum number of results to return

        Returns:
            Search results with assigned tasks
        """
        return self.search_tasks(
            query_key="assigned", attachments=attachments, limit=limit
        )

    def search_authored_tasks(
        self, attachments: Optional[ManiphestSearchAttachments] = None, limit: int = 100
    ) -> ManiphestSearchResults:
        """
        Search for tasks authored by the current user.

        Args:
            attachments: Additional data to include in results
            limit: Maximum number of results to return

        Returns:
            Search results with authored tasks
        """
        return self.search_tasks(
            query_key="authored", attachments=attachments, limit=limit
        )

    def search_tasks_by_status(
        self,
        statuses: List[str],
        attachments: Optional[ManiphestSearchAttachments] = None,
        limit: int = 100,
    ) -> ManiphestSearchResults:
        """
        Search for tasks with specific statuses.

        Args:
            statuses: List of status names to search for
            attachments: Additional data to include in results
            limit: Maximum number of results to return

        Returns:
            Search results with tasks matching the statuses
        """
        return self.search_tasks(
            constraints={"statuses": statuses}, attachments=attachments, limit=limit
        )

    def search_tasks_by_project(
        self,
        projects: List[str],
        attachments: Optional[ManiphestSearchAttachments] = None,
        limit: int = 100,
    ) -> ManiphestSearchResults:
        """
        Search for tasks tagged with specific projects.

        Args:
            projects: List of project names or PHIDs
            attachments: Additional data to include in results
            limit: Maximum number of results to return

        Returns:
            Search results with tasks tagged with the projects
        """
        return self.search_tasks(
            constraints={"projects": projects}, attachments=attachments, limit=limit
        )

    def search_tasks_by_assignee(
        self,
        assignees: List[str],
        attachments: Optional[ManiphestSearchAttachments] = None,
        limit: int = 100,
    ) -> ManiphestSearchResults:
        """
        Search for tasks assigned to specific users.

        Args:
            assignees: List of usernames or PHIDs
            attachments: Additional data to include in results
            limit: Maximum number of results to return

        Returns:
            Search results with tasks assigned to the users
        """
        return self.search_tasks(
            constraints={"assigned": assignees}, attachments=attachments, limit=limit
        )

    def fulltext_search_tasks(
        self,
        query: str,
        attachments: Optional[ManiphestSearchAttachments] = None,
        limit: int = 100,
    ) -> ManiphestSearchResults:
        """
        Perform fulltext search on tasks.

        Args:
            query: Search query string
            attachments: Additional data to include in results
            limit: Maximum number of results to return

        Returns:
            Search results ordered by relevance
        """
        return self.search_tasks(
            constraints={"query": query},
            order="relevance",
            attachments=attachments,
            limit=limit,
        )
