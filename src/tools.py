"""
MCP tools for Phabricator API operations.

This module contains all the MCP tool definitions for interacting with
Phabricator/Phorge through the Conduit API.
"""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from fastmcp import FastMCP

from src.client import PhabricatorAPIError
from src.client.types import (
    ManiphestSearchAttachments,
    ManiphestSearchConstraints,
    ManiphestTaskTransactionComment,
    ManiphestTaskTransactionDescription,
    ManiphestTaskTransactionOwner,
    ManiphestTaskTransactionPriority,
    ManiphestTaskTransactionStatus,
    ManiphestTaskTransactionTitle,
)
from src.client.unified import PhabricatorClient


def handle_api_errors(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        try:
            result = func(*args, **kwargs)
            # If the function returns a dict with 'success' key, return as-is
            # Otherwise, wrap the result in a success response
            if isinstance(result, dict) and "success" in result:
                return result
            return {"success": True, "result": result}
        except PhabricatorAPIError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, "error_code", None),
            }
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    return wrapper


def register_tools(  # noqa: C901
    mcp: FastMCP, get_client_func: Callable[[], PhabricatorClient]
) -> None:
    @mcp.tool()
    @handle_api_errors
    def whoami() -> dict:
        """
        Get the current user's information.

        Returns:
            User information
        """
        client = get_client_func()
        result = client.user.whoami()
        return {"success": True, "user": result}

    @mcp.tool()
    @handle_api_errors
    def create_phabricator_task(
        title: str, description: str = "", owner_phid: str = ""
    ) -> dict:
        client = get_client_func()
        result = client.maniphest.create_task(
            title=title,
            description=description,
            owner_phid=owner_phid,
        )
        return {"success": True, "task": result}

    @mcp.tool()
    @handle_api_errors
    def get_phabricator_task(task_id: int) -> dict:
        """
        Get details of a specific Phabricator task

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            Task details
        """
        client = get_client_func()
        result = client.maniphest.get_task(task_id)
        return {"success": True, "task": result}

    @mcp.tool()
    @handle_api_errors
    def phabricator_task_set_subtask(task_id: str, subtask_ids: str) -> dict:
        """
        Set a subtask to a Phabricator task

        Args:
            task_id: The ID, PHID of the parent task
            subtask_id: The ID, PHID of the subtask to set, commas separated

        Returns:
            Success status
        """
        client = get_client_func()
        client.maniphest.edit_task(
            object_identifier=task_id,
            transactions=[
                {
                    "type": "subtasks.set",
                    "value": [
                        subtask.strip()
                        for subtask in subtask_ids.split(",")
                        if subtask.strip()
                    ],
                }
            ],
        )
        return {"success": True}

    @mcp.tool()
    @handle_api_errors
    def phabricator_task_set_parent(task_id: str, parent_ids: str) -> dict:
        """
        Set a parent task to a Phabricator task

        Args:
            task_id: The ID, PHID of the child task
            parent_ids: The ID, PHID of the parent task to set, commas separated

        Returns:
            Success status
        """
        client = get_client_func()
        client.maniphest.edit_task(
            object_identifier=task_id,
            transactions=[
                {
                    "type": "parents.set",
                    "value": [
                        parent.strip()
                        for parent in parent_ids.split(",")
                        if parent.strip()
                    ],
                }
            ],
        )
        return {"success": True}

    @mcp.tool()
    @handle_api_errors
    def phabricator_task_update_metadata(
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        owner_phid: Optional[str] = None,
    ) -> dict:
        """
        Update the metadata of a Phabricator task.

        Args:
            task_id: The ID, PHID of the task to update.
            title: The new title for the task.
            description: The new description for the task.
            priority: The new priority for the task.
            status: The new status for the task.
            owner_phid: The PHID of the new owner for the task.


        Returns:
            Success status.
        """
        client = get_client_func()

        transactions = []
        if title is not None:
            transactions.append(
                ManiphestTaskTransactionTitle(type="title", value=title)
            )
        if description is not None:
            transactions.append(
                ManiphestTaskTransactionDescription(
                    type="description", value=description
                )
            )
        if priority is not None:
            transactions.append(
                ManiphestTaskTransactionPriority(type="priority", value=priority)
            )
        if status is not None:
            transactions.append(
                ManiphestTaskTransactionStatus(type="status", value=status)
            )
        if owner_phid is not None:
            transactions.append(
                ManiphestTaskTransactionOwner(type="owner", value=owner_phid)
            )

        client.maniphest.edit_task(
            object_identifier=task_id,
            transactions=transactions,
        )
        return {"success": True}

    @mcp.tool()
    @handle_api_errors
    def phabricator_task_add_comment(task_id: str, comment: str) -> dict:
        """
        Add a comment to a Phabricator task.

        Args:
            task_id: The ID, PHID of the task to add the comment to.
            comment: The content of the comment.

        Returns:
            Success status.
        """
        client = get_client_func()
        client.maniphest.edit_task(
            object_identifier=task_id,
            transactions=[
                ManiphestTaskTransactionComment(
                    type="comment",
                    value=comment,
                )
            ],
        )
        return {"success": True}

    @mcp.tool()
    @handle_api_errors
    def search_phabricator_tasks(
        query_key: str = "",
        ids: List[int] = [],
        phids: List[str] = [],
        assigned: List[str] = [],
        author_phids: List[str] = [],
        statuses: List[str] = [],
        priorities: List[int] = [],
        projects: List[str] = [],
        subscribers: List[str] = [],
        fulltext_query: str = "",
        has_parents: bool = None,
        has_subtasks: bool = None,
        created_after: int = None,
        created_before: int = None,
        modified_after: int = None,
        modified_before: int = None,
        order: str = "",
        include_subscribers: bool = False,
        include_projects: bool = False,
        include_columns: bool = False,
        limit: int = 100,
    ) -> dict:
        """
        Search for Phabricator tasks with advanced filtering and search capabilities.

        Args:
            query_key: Builtin query ("assigned", "authored", "subscribed", "open", "all")
            ids: List of specific task IDs to search for
            phids: List of specific task PHIDs to search for
            assigned: List of usernames or PHIDs of assignees
            author_phids: List of PHIDs of task authors
            statuses: List of task statuses to filter by
            priorities: List of priority levels to filter by
            projects: List of project names or PHIDs to filter by
            subscribers: List of subscriber usernames or PHIDs
            fulltext_query: Full-text search query string
            has_parents: Filter by whether tasks have parent tasks
            has_subtasks: Filter by whether tasks have subtasks
            created_after: Unix timestamp - tasks created after this time
            created_before: Unix timestamp - tasks created before this time
            modified_after: Unix timestamp - tasks modified after this time
            modified_before: Unix timestamp - tasks modified before this time
            order: Result ordering ("priority", "updated", "newest", "oldest", "closed", "title", "relevance")
            include_subscribers: Include subscriber information in results
            include_projects: Include project information in results
            include_columns: Include workboard column information in results
            limit: Maximum number of results to return (default: 100)

        Returns:
            Search results with task data and metadata
        """
        client = get_client_func()

        # Build constraints
        constraints: ManiphestSearchConstraints = {}

        if ids:
            constraints["ids"] = ids
        if phids:
            constraints["phids"] = phids
        if assigned:
            constraints["assigned"] = assigned
        if author_phids:
            constraints["authorPHIDs"] = author_phids
        if statuses:
            constraints["statuses"] = statuses
        if priorities:
            constraints["priorities"] = priorities
        if projects:
            constraints["projects"] = projects
        if subscribers:
            constraints["subscribers"] = subscribers
        if fulltext_query:
            constraints["query"] = fulltext_query
        if has_parents is not None:
            constraints["hasParents"] = has_parents
        if has_subtasks is not None:
            constraints["hasSubtasks"] = has_subtasks
        if created_after:
            constraints["createdStart"] = created_after
        if created_before:
            constraints["createdEnd"] = created_before
        if modified_after:
            constraints["modifiedStart"] = modified_after
        if modified_before:
            constraints["modifiedEnd"] = modified_before

        # Build attachments
        attachments: ManiphestSearchAttachments = {}
        if include_subscribers:
            attachments["subscribers"] = True
        if include_projects:
            attachments["projects"] = True
        if include_columns:
            attachments["columns"] = True

        result = client.maniphest.search_tasks(
            query_key=query_key or None,
            constraints=constraints if constraints else None,
            attachments=attachments if attachments else None,
            order=order or None,
            limit=limit,
        )

        return {"success": True, "results": result}

    @mcp.tool()
    @handle_api_errors
    def get_my_assigned_tasks(
        include_projects: bool = True,
        include_subscribers: bool = False,
        limit: int = 50,
    ) -> dict:
        """
        Get tasks assigned to the current user.

        Args:
            include_projects: Include project information in results
            include_subscribers: Include subscriber information in results
            limit: Maximum number of results to return

        Returns:
            Tasks assigned to the current user
        """
        client = get_client_func()

        attachments: ManiphestSearchAttachments = {}
        if include_projects:
            attachments["projects"] = True
        if include_subscribers:
            attachments["subscribers"] = True

        result = client.maniphest.search_assigned_tasks(
            attachments=attachments if attachments else None, limit=limit
        )

        return {"success": True, "assigned_tasks": result}

    @mcp.tool()
    @handle_api_errors
    def get_my_authored_tasks(
        include_projects: bool = True,
        include_subscribers: bool = False,
        limit: int = 50,
    ) -> dict:
        """
        Get tasks authored by the current user.

        Args:
            include_projects: Include project information in results
            include_subscribers: Include subscriber information in results
            limit: Maximum number of results to return

        Returns:
            Tasks authored by the current user
        """
        client = get_client_func()

        attachments: ManiphestSearchAttachments = {}
        if include_projects:
            attachments["projects"] = True
        if include_subscribers:
            attachments["subscribers"] = True

        result = client.maniphest.search_authored_tasks(
            attachments=attachments if attachments else None, limit=limit
        )

        return {"success": True, "authored_tasks": result}

    @mcp.tool()
    @handle_api_errors
    def search_tasks_by_project(
        project_names: List[str],
        status_filter: str = "open",
        include_subscribers: bool = False,
        order: str = "priority",
        limit: int = 50,
    ) -> dict:
        """
        Search for tasks in specific projects.

        Args:
            project_names: List of project names or PHIDs to search in
            status_filter: Status filter ("open", "resolved", "all")
            include_subscribers: Include subscriber information in results
            order: Result ordering ("priority", "updated", "newest", "oldest")
            limit: Maximum number of results to return

        Returns:
            Tasks in the specified projects
        """
        client = get_client_func()

        # Build constraints
        constraints: ManiphestSearchConstraints = {"projects": project_names}

        if status_filter != "all":
            if status_filter == "open":
                constraints["statuses"] = ["open"]
            elif status_filter == "resolved":
                constraints["statuses"] = ["resolved"]

        # Build attachments
        attachments: ManiphestSearchAttachments = {"projects": True}
        if include_subscribers:
            attachments["subscribers"] = True

        result = client.maniphest.search_tasks(
            constraints=constraints, attachments=attachments, order=order, limit=limit
        )

        return {"success": True, "project_tasks": result}

    @mcp.tool()
    @handle_api_errors
    def search_high_priority_tasks(
        assignee_filter: List[str] = [],
        project_filter: List[str] = [],
        include_projects: bool = True,
        limit: int = 30,
    ) -> dict:
        """
        Search for high priority tasks.

        Args:
            assignee_filter: List of usernames/PHIDs to filter by assignee (empty = all)
            project_filter: List of project names/PHIDs to filter by project (empty = all)
            include_projects: Include project information in results
            limit: Maximum number of results to return

        Returns:
            High priority tasks
        """
        client = get_client_func()

        # Build constraints for high priority tasks
        constraints: ManiphestSearchConstraints = {
            "priorities": [90, 100]  # High and Unbreak Now priorities
        }

        if assignee_filter:
            constraints["assigned"] = assignee_filter
        if project_filter:
            constraints["projects"] = project_filter

        # Build attachments
        attachments: ManiphestSearchAttachments = {}
        if include_projects:
            attachments["projects"] = True

        result = client.maniphest.search_tasks(
            constraints=constraints,
            attachments=attachments if attachments else None,
            order="priority",
            limit=limit,
        )

        return {"success": True, "high_priority_tasks": result}

    @mcp.tool()
    @handle_api_errors
    def search_recently_updated_tasks(
        days_back: int = 7,
        include_projects: bool = True,
        include_subscribers: bool = False,
        limit: int = 50,
    ) -> dict:
        """
        Search for tasks updated in the last N days.

        Args:
            days_back: Number of days to look back for updates
            include_projects: Include project information in results
            include_subscribers: Include subscriber information in results
            limit: Maximum number of results to return

        Returns:
            Recently updated tasks
        """
        import time

        client = get_client_func()

        # Calculate timestamp for N days ago
        days_back_timestamp = int(time.time()) - (days_back * 24 * 60 * 60)

        constraints: ManiphestSearchConstraints = {"modifiedStart": days_back_timestamp}

        # Build attachments
        attachments: ManiphestSearchAttachments = {}
        if include_projects:
            attachments["projects"] = True
        if include_subscribers:
            attachments["subscribers"] = True

        result = client.maniphest.search_tasks(
            constraints=constraints,
            attachments=attachments if attachments else None,
            order="updated",
            limit=limit,
        )

        return {"success": True, "recently_updated_tasks": result}
