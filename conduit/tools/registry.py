from typing import Callable, Optional

from fastmcp import FastMCP

from conduit.client.types import (
    ManiphestSearchAttachments,
    ManiphestSearchConstraints,
    ManiphestTaskTransactionComment,
    ManiphestTaskTransactionDescription,
    ManiphestTaskTransactionOwner,
    ManiphestTaskTransactionPriority,
    ManiphestTaskTransactionStatus,
    ManiphestTaskTransactionTitle,
    UserSearchAttachments,
    UserSearchConstraints,
)
from conduit.client.unified import PhabricatorClient
from conduit.tools.handlers import handle_api_errors
from conduit.tools.optimization import optimize_token_usage


def _add_pagination_metadata(result: dict, cursor: dict = None) -> dict:
    """
    Add pagination metadata to search results.

    Args:
        result: Original search result
        cursor: Pagination cursor from API

    Returns:
        Result with enhanced pagination metadata
    """
    if cursor:
        result["pagination"] = {
            "cursor": cursor,
            "has_more": cursor.get("after") is not None,
            "limit": cursor.get("limit", 100),
        }

    return result


def register_tools(  # noqa: C901
    mcp: FastMCP,
    get_client_func: Callable[[], PhabricatorClient],
    enable_type_safety: bool = False,
) -> None:
    """
    Register all MCP tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
        get_client_func: Function to get Phabricator client instance
        enable_type_safety: Whether to enable type-safe client wrapper
    """

    @mcp.tool()
    @handle_api_errors
    def pha_user_whoami(enable_type_safety: bool = False) -> dict:
        """
        Get the current user's information.

        Args:
            enable_type_safety: Enable runtime type validation

        Returns:
            User information
        """
        client = get_client_func()

        # Apply type safety if requested
        if enable_type_safety:
            try:
                from conduit.utils import RuntimeValidationClient

                type_safe_client = RuntimeValidationClient(client)
                result = type_safe_client.get_user_info(client.user.whoami()["phid"])
            except ImportError:
                # Fallback to regular client if type_safe module not available
                result = client.user.whoami()
        else:
            result = client.user.whoami()

        return {"success": True, "user": result}

    @mcp.tool()
    @handle_api_errors
    @optimize_token_usage
    def pha_user_search(
        query_key: str = "",
        ids: Optional[list[int]] = None,
        phids: Optional[list[str]] = None,
        usernames: Optional[list[str]] = None,
        name_like: str = "",
        is_admin: bool = None,
        is_disabled: bool = None,
        is_bot: bool = None,
        is_mailing_list: bool = None,
        needs_approval: bool = None,
        mfa: bool = None,
        created_start: int = None,
        created_end: int = None,
        fulltext_query: str = "",
        order: str = "",
        include_availability: bool = False,
        limit: int = 100,
        max_tokens: int = 5000,
        enable_type_safety: bool = False,
    ) -> dict:
        """
        Search for users with advanced filtering capabilities and token optimization.

        Args:
            query_key: Builtin query ("active", "admin", "all", "approval")
            ids: List of specific user IDs to search for
            phids: List of specific user PHIDs to search for
            usernames: List of exact usernames to find
            name_like: Find users whose usernames or real names contain this substring
            is_admin: Pass true to find only administrators, or false to omit administrators
            is_disabled: Pass true to find only disabled users, or false to omit disabled users
            is_bot: Pass true to find only bots, or false to omit bots
            is_mailing_list: Pass true to find only mailing lists, or false to omit mailing lists
            needs_approval: Pass true to find only users awaiting approval, or false to omit these users
            mfa: Pass true to find only users enrolled in MFA, or false to omit these users
            created_start: Unix timestamp - find users created after this time
            created_end: Unix timestamp - find users created before this time
            fulltext_query: Full-text search query string
            order: Result ordering ("newest", "oldest", "relevance")
            include_availability: Include user availability information in results
            limit: Maximum number of results to return (default: 100, max: 1000)
            max_tokens: Maximum token budget for response (default: 5000)
            enable_type_safety: Enable runtime type validation

        Returns:
            Search results with user data, pagination metadata, and token optimization info
        """
        # Initialize None parameters to empty lists
        if ids is None:
            ids = []
        if phids is None:
            phids = []
        if usernames is None:
            usernames = []

        client = get_client_func()

        # Build constraints
        constraints: UserSearchConstraints = {}

        if ids:
            constraints["ids"] = ids
        if phids:
            constraints["phids"] = phids
        if usernames:
            constraints["usernames"] = usernames
        if name_like:
            constraints["nameLike"] = name_like
        if is_admin is not None:
            constraints["isAdmin"] = is_admin
        if is_disabled is not None:
            constraints["isDisabled"] = is_disabled
        if is_bot is not None:
            constraints["isBot"] = is_bot
        if is_mailing_list is not None:
            constraints["isMailingList"] = is_mailing_list
        if needs_approval is not None:
            constraints["needsApproval"] = needs_approval
        if mfa is not None:
            constraints["mfa"] = mfa
        if created_start is not None:
            constraints["createdStart"] = created_start
        if created_end is not None:
            constraints["createdEnd"] = created_end
        if fulltext_query:
            constraints["query"] = fulltext_query

        # Build attachments
        attachments: UserSearchAttachments = {}
        if include_availability:
            attachments["availability"] = True

        # Apply type safety if requested
        if enable_type_safety:
            try:
                from conduit.utils import RuntimeValidationClient

                type_safe_client = RuntimeValidationClient(client)

                # Build constraints for type-safe client
                type_safe_constraints = {}
                if ids:
                    type_safe_constraints["ids"] = ids
                if phids:
                    type_safe_constraints["phids"] = phids
                if usernames:
                    type_safe_constraints["usernames"] = usernames
                if name_like:
                    type_safe_constraints["nameLike"] = name_like
                if is_admin is not None:
                    type_safe_constraints["isAdmin"] = is_admin
                if is_disabled is not None:
                    type_safe_constraints["isDisabled"] = is_disabled
                if is_bot is not None:
                    type_safe_constraints["isBot"] = is_bot
                if is_mailing_list is not None:
                    type_safe_constraints["isMailingList"] = is_mailing_list
                if needs_approval is not None:
                    type_safe_constraints["needsApproval"] = needs_approval
                if mfa is not None:
                    type_safe_constraints["mfa"] = mfa
                if created_start is not None:
                    type_safe_constraints["createdStart"] = created_start
                if created_end is not None:
                    type_safe_constraints["createdEnd"] = created_end
                if fulltext_query:
                    type_safe_constraints["query"] = fulltext_query

                result = type_safe_client.search_users(
                    constraints=(
                        type_safe_constraints if type_safe_constraints else None
                    ),
                    limit=limit,
                )
            except ImportError:
                # Fallback to regular client if type_safe module not available
                result = client.user.search(
                    query_key=query_key or None,
                    constraints=constraints if constraints else None,
                    attachments=attachments if attachments else None,
                    order=order or None,
                    limit=limit,
                )
        else:
            # Call the search API
            result = client.user.search(
                query_key=query_key or None,
                constraints=constraints if constraints else None,
                attachments=attachments if attachments else None,
                order=order or None,
                limit=limit,
            )

        # Apply token optimization
        if max_tokens and result.get("data"):
            data = result["data"]
            if len(data) > 20:  # Further reduce limit for token optimization
                result["data"] = data[:20]
                result["token_optimization"] = {
                    "applied": True,
                    "original_count": len(data),
                    "returned_count": 20,
                    "reason": "Token budget optimization",
                }

        return {
            "success": True,
            "users": result["data"],
            "cursor": result.get("cursor"),
        }

    @mcp.tool()
    @handle_api_errors
    def pha_task_create(
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
    def pha_task_get(task_id: int) -> dict:
        """
        Get details of a specific Phabricator task

        Args:
            task_id: The ID of the task to retrieve, e.g. 1234

        Returns:
            Task details
        """
        client = get_client_func()
        result = client.maniphest.get_task(task_id)
        return {"success": True, "task": result}

    @mcp.tool()
    @handle_api_errors
    def pha_task_update(
        task_id: str,
        title: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        owner_phid: str | None = None,
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
    def pha_task_add_comment(task_id: str, comment: str) -> dict:
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
    def pha_task_get_personal(
        task_type: str = "assigned",
        include_projects: bool = True,
        include_subscribers: bool = False,
        limit: int = 50,
    ) -> dict:
        """
        Get personal tasks assigned to or authored by the current user.

        Args:
            task_type: Type of tasks to retrieve ("assigned" or "authored")
            include_projects: Include project information in results
            include_subscribers: Include subscriber information in results
            limit: Maximum number of results to return

        Returns:
            Personal tasks based on the specified type
        """
        client = get_client_func()

        attachments: ManiphestSearchAttachments = {}
        if include_projects:
            attachments["projects"] = True
        if include_subscribers:
            attachments["subscribers"] = True

        if task_type == "assigned":
            result = client.maniphest.search_assigned_tasks(
                attachments=attachments if attachments else None, limit=limit
            )
            return {"success": True, "assigned_tasks": result}
        elif task_type == "authored":
            result = client.maniphest.search_authored_tasks(
                attachments=attachments if attachments else None, limit=limit
            )
            return {"success": True, "authored_tasks": result}
        else:
            return {
                "success": False,
                "error": "Invalid task_type. Use 'assigned' or 'authored'",
            }

    @mcp.tool()
    @handle_api_errors
    def pha_task_update_relationships(
        task_id: str,
        relationship_type: str,
        target_ids: list[str],
    ) -> dict:
        """
        Update task relationships (subtasks or parents).

        Args:
            task_id: The ID, PHID of the task to update
            relationship_type: Type of relationship ("subtask" or "parent")
            target_ids: List of target task IDs/PHIDs, comma separated

        Returns:
            Success status
        """
        client = get_client_func()

        # Parse comma-separated target IDs
        target_list = [
            target.strip() for target in target_ids.split(",") if target.strip()
        ]

        if not target_list:
            return {"success": False, "error": "No valid target IDs provided"}

        if relationship_type == "subtask":
            transaction_type = "subtasks.set"
        elif relationship_type == "parent":
            transaction_type = "parents.set"
        else:
            return {
                "success": False,
                "error": "Invalid relationship_type. Use 'subtask' or 'parent'",
            }

        client.maniphest.edit_task(
            object_identifier=task_id,
            transactions=[
                {
                    "type": transaction_type,
                    "value": target_list,
                }
            ],
        )
        return {"success": True}

    @mcp.tool()
    @handle_api_errors
    @optimize_token_usage
    def pha_task_search_advanced(
        query_key: str = "",
        assigned: Optional[list[str]] = None,
        author_phids: Optional[list[str]] = None,
        statuses: Optional[list[str]] = None,
        priorities: Optional[list[int]] = None,
        projects: Optional[list[str]] = None,
        subscribers: Optional[list[str]] = None,
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
        preset: str | None = None,
        max_tokens: int = 5000,
    ) -> dict:
        """
        Advanced task search with filtering, preset options, and token optimization.

        Args:
            query_key: Builtin query ("assigned", "authored", "subscribed", "open", "all")
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
            limit: Maximum number of results to return (default: 100, max: 1000)
            preset: Preset search configurations for common use cases
            max_tokens: Maximum token budget for response (default: 5000)

        Returns:
            Search results with task data, pagination metadata, and token optimization info
        """
        # Initialize None parameters to empty lists
        if assigned is None:
            assigned = []
        if author_phids is None:
            author_phids = []
        if statuses is None:
            statuses = []
        if priorities is None:
            priorities = []
        if projects is None:
            projects = []
        if subscribers is None:
            subscribers = []

        client = get_client_func()

        # Handle preset configurations
        if preset:
            if preset == "assigned":
                query_key = "assigned"
                if not assigned:
                    # Get current user for assigned tasks
                    user_info = client.user.whoami()
                    assigned = [user_info["phid"]]
            elif preset == "authored":
                query_key = "authored"
                if not author_phids:
                    # Get current user for authored tasks
                    user_info = client.user.whoami()
                    author_phids = [user_info["phid"]]
            elif preset == "high_priority":
                priorities = [90, 100]  # High and Unbreak Now priorities
                order = "priority"
            elif preset == "recent":
                import time

                modified_after = int(time.time()) - (7 * 24 * 60 * 60)  # Last 7 days
                order = "updated"
            elif preset == "open":
                statuses = ["open"]
            elif preset == "all":
                query_key = "all"

        # Build constraints
        constraints: ManiphestSearchConstraints = {}

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

        # Apply token optimization
        if max_tokens and result.get("data"):
            data = result["data"]
            if len(data) > 15:  # Further reduce limit for token optimization
                result["data"] = data[:15]
                result["token_optimization"] = {
                    "applied": True,
                    "original_count": len(data),
                    "returned_count": 15,
                    "reason": "Token budget optimization",
                }

        # Add pagination metadata
        result = _add_pagination_metadata(result, result.get("cursor"))

        return {"success": True, "results": result}

    # Register remaining tools in other modules
    from conduit.tools.diffusion_tools import register_diffusion_tools
    from conduit.tools.differential_tools import register_differential_tools

    register_diffusion_tools(mcp, get_client_func, enable_type_safety)
    register_differential_tools(mcp, get_client_func, enable_type_safety)
