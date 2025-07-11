"""
MCP tools for Phabricator API operations.

This module contains all the MCP tool definitions for interacting with
Phabricator/Phorge through the Conduit API.
"""

from functools import wraps
from typing import Any, Callable, Dict

from fastmcp import FastMCP

from src.client import PhabricatorAPIError
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
