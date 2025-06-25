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
    def whoami() -> dict:
        """
        Get the current user's information.

        Returns:
            User information
        """
        try:
            client = get_client_func()
            result = client.user.whoami()

            return {"success": True, "user": result}
        except PhabricatorAPIError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, "error_code", None),
            }
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    @mcp.tool()
    def create_phabricator_task(
        title: str, description: str = "", owner_phid: str = ""
    ) -> dict:
        try:
            client = get_client_func()

            result = client.maniphest.create_task(
                title=title,
                description=description,
                owner_phid=owner_phid,
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
            result = client.maniphest.get_task(task_id)

            return {"success": True, "task": result}
        except PhabricatorAPIError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, "error_code", None),
            }
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
