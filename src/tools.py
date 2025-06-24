"""
MCP tools for Phabricator API operations.

This module contains all the MCP tool definitions for interacting with
Phabricator/Phorge through the Conduit API.
"""

from typing import Callable

from fastmcp import FastMCP

from src.client import PhabricatorAPIError
from src.client.unified import PhabricatorClient


def register_tools(  # noqa: C901
    mcp: FastMCP, get_client_func: Callable[[], PhabricatorClient]
) -> None:
    @mcp.tool()
    def create_phabricator_task(
        title: str, description: str = "", owner_phid: str = ""
    ) -> dict:
        """
        Create a Phabricator Task

        Args:
            title: The title of a Phabricator Task
            description: The description of a Phabricator Task. Support Phabricator Markdown.
            owner_phid: The owner PhID of a Phabricator Task, e.g. PHID-USER-l2wrse2ie7qsjldx5ake. If not sure, please left this field blank.

        Returns:
            The created task information
        """
        try:
            client = get_client_func()

            # If owner_phid is empty string, set to None
            owner = owner_phid if owner_phid.strip() else None

            result = client.create_task(
                title=title, description=description, owner_phid=owner
            )

            return {"success": True, "task": result}
        except PhabricatorAPIError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, "error_code", None),
            }
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    def search_phabricator_tasks(
        query: str = "", status: str = "open", limit: int = 20
    ) -> dict:
        """
        Search for Phabricator tasks

        Args:
            query: Search query for task titles/descriptions
            status: Task status filter ('open', 'resolved', 'wontfix', 'invalid', 'duplicate', 'spite')
            limit: Maximum number of tasks to return (default: 20, max: 100)

        Returns:
            List of matching tasks
        """
        try:
            client = get_client_func()

            constraints = {}

            if query:
                constraints["query"] = query

            if status:
                status_map = {
                    "open": ["open"],
                    "resolved": ["resolved"],
                    "wontfix": ["wontfix"],
                    "invalid": ["invalid"],
                    "duplicate": ["duplicate"],
                    "spite": ["spite"],
                }
                if status in status_map:
                    constraints["statuses"] = status_map[status]

            # Limit the results to prevent too much data
            limit = min(limit, 100)

            result = client.search_tasks(constraints=constraints, limit=limit)

            return {
                "success": True,
                "tasks": result.get("data", []),
                "cursor": result.get("cursor", {}),
            }
        except PhabricatorAPIError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, "error_code", None),
            }
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    def get_phabricator_task(task_id: int) -> dict:
        """
        Get details of a specific Phabricator task

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            Task details
        """
        try:
            client = get_client_func()
            result = client.get_task(task_id)

            return {"success": True, "task": result}
        except PhabricatorAPIError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, "error_code", None),
            }
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    def test_phabricator_connection() -> dict:
        """
        Test the connection to Phabricator API

        Returns:
            Connection status and user information
        """
        try:
            client = get_client_func()
            result = client.test_connection()

            return {"success": True, "connection": "OK", "user": result}
        except PhabricatorAPIError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, "error_code", None),
            }
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
