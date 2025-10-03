from functools import wraps
from typing import Any, Callable, List, Literal, Optional

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


# Pagination and Token Optimization Functions


def _apply_smart_pagination(data: List[Any], limit: int = None) -> dict:
    """
    Apply smart pagination to data with token optimization.

    Args:
        data: List of data items
        limit: Maximum number of items to return (optional)

    Returns:
        Paginated response with metadata
    """
    if limit is None:
        limit = 100  # Default limit

    # Apply limit if data is larger than limit
    if len(data) > limit:
        paginated_data = data[:limit]
        has_more = True
        total_count = len(data)
        suggestion = f"Use pagination to retrieve remaining {total_count - limit} items"
    else:
        paginated_data = data
        has_more = False
        total_count = len(data)
        suggestion = None

    return {
        "data": paginated_data,
        "pagination": {
            "total": total_count,
            "returned": len(paginated_data),
            "has_more": has_more,
        },
        "suggestion": suggestion,
    }


def optimize_token_usage(func: Callable) -> Callable:
    """
    Decorator to optimize token usage by applying smart limits and truncation.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # Apply token optimization to search results
        if isinstance(result, dict) and "data" in result:
            # Check if this is a search result that needs optimization
            data = result["data"]
            if isinstance(data, list) and len(data) > 50:
                # Apply smart pagination
                optimized_result = _apply_smart_pagination(
                    data, kwargs.get("limit", 100)
                )
                result.update(optimized_result)

        return result

    return wrapper


def _truncate_text_response(text: str, max_length: int = 2000) -> dict:
    """
    Truncate long text responses with helpful guidance.

    Args:
        text: The text to truncate
        max_length: Maximum allowed length

    Returns:
        Truncated response with guidance
    """
    if len(text) <= max_length:
        return {"content": text, "truncated": False}

    truncated_text = text[:max_length]
    remaining_length = len(text) - max_length

    return {
        "content": truncated_text,
        "truncated": True,
        "original_length": len(text),
        "remaining_length": remaining_length,
        "suggestion": f"Content was truncated. {remaining_length} characters remaining. Use specific search parameters to reduce results.",
    }


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
                from conduit.utils.validation import RuntimeValidationClient

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
        ids: List[int] = [],
        phids: List[str] = [],
        usernames: List[str] = [],
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

        Returns:
            Search results with user data, pagination metadata, and token optimization info
        """
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
                from conduit.utils.validation import RuntimeValidationClient

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

        # Add pagination metadata
        result = _add_pagination_metadata(result, result.get("cursor"))

        return {"success": True, "users": result["data"], "cursor": result["cursor"]}

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
        task_type: Literal["assigned", "authored"] = "assigned",
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
        relationship_type: Literal["subtask", "parent"],
        target_ids: List[str],
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
        preset: Literal[
            "all", "assigned", "authored", "open", "high_priority", "recent"
        ] = None,
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

    # Diffusion (Repository) Tools

    @mcp.tool()
    @handle_api_errors
    @optimize_token_usage
    def pha_repository_search(
        name_contains: str = "",
        vcs_type: str = "",
        status: str = "",
        limit: int = 50,
        max_tokens: int = 5000,
    ) -> dict:
        """
        Search for repositories in Phabricator with token optimization.

        Args:
            name_contains: Filter repositories by name containing this string
            vcs_type: Filter by version control system ("git", "hg", "svn")
            status: Filter by repository status ("active", "inactive")
            limit: Maximum number of results to return (default: 50, max: 500)
            max_tokens: Maximum token budget for response (default: 5000)

        Returns:
            List of repositories matching the criteria with pagination metadata
        """
        client = get_client_func()

        constraints = {}
        if name_contains:
            constraints["name"] = name_contains
        if vcs_type:
            constraints["vcs"] = vcs_type
        if status:
            constraints["status"] = status

        result = client.diffusion.search_repositories(
            constraints=constraints if constraints else None, limit=limit
        )

        # Apply token optimization
        if max_tokens and result.get("data"):
            data = result["data"]
            if len(data) > 10:  # Further reduce limit for token optimization
                result["data"] = data[:10]
                result["token_optimization"] = {
                    "applied": True,
                    "original_count": len(data),
                    "returned_count": 10,
                    "reason": "Token budget optimization",
                }

        # Add pagination metadata
        result = _add_pagination_metadata(result, result.get("cursor"))

        return {"success": True, "repositories": result}

    @mcp.tool()
    @handle_api_errors
    def pha_repository_create(
        name: str,
        vcs_type: str = "git",
        description: str = "",
        callsign: str = "",
    ) -> dict:
        """
        Create a new repository in Phabricator.

        Args:
            name: Repository name
            vcs_type: Version control system type ("git", "hg", "svn")
            description: Repository description
            callsign: Optional repository callsign

        Returns:
            Created repository information
        """
        client = get_client_func()

        result = client.diffusion.create_repository(
            name=name,
            vcs_type=vcs_type,
            description=description,
            callsign=callsign if callsign else None,
        )

        return {"success": True, "repository": result}

    @mcp.tool()
    @handle_api_errors
    def pha_repository_info(repository_identifier: str) -> dict:
        """
        Get detailed information about a specific repository.

        Args:
            repository_identifier: Repository ID, PHID, callsign, or name

        Returns:
            Repository information
        """
        client = get_client_func()

        # Try different search strategies based on identifier format
        result = None

        # 1. If it looks like a PHID, search by PHID
        if repository_identifier.startswith("PHID-REPO-"):
            result = client.diffusion.search_repositories(
                constraints={"phids": [repository_identifier]},
                limit=1,
            )

        # 2. If it's numeric, search by ID
        elif repository_identifier.isdigit():
            result = client.diffusion.search_repositories(
                constraints={"ids": [int(repository_identifier)]},
                limit=1,
            )

        # 3. If it's all uppercase, likely a callsign
        elif repository_identifier.isupper() and repository_identifier.isalpha():
            result = client.diffusion.search_repositories(
                constraints={"callsigns": [repository_identifier]},
                limit=1,
            )

        # 4. Try searching by short name
        if not result or not result.get("data"):
            try:
                result = client.diffusion.search_repositories(
                    constraints={"shortNames": [repository_identifier]},
                    limit=1,
                )
            except Exception:
                # shortNames constraint might fail, continue to next strategy
                pass

        # 5. If still no results, do a general search and filter by name
        if not result or not result.get("data"):
            # Search all repositories and find by name match
            all_repos = client.diffusion.search_repositories(limit=100)
            for repo in all_repos.get("data", []):
                fields = repo.get("fields", {})
                if (
                    fields.get("name") == repository_identifier
                    or fields.get("shortName") == repository_identifier
                    or fields.get("callsign") == repository_identifier
                ):
                    result = {"data": [repo]}
                    break

        if result and result.get("data"):
            return {"success": True, "repository": result["data"][0]}
        else:
            return {
                "success": False,
                "error": f"Repository '{repository_identifier}' not found",
            }

    @mcp.tool()
    @handle_api_errors
    @optimize_token_usage
    def pha_repository_browse(
        repository: str,
        path: str = "/",
        commit: str = "",
        max_tokens: int = 5000,
    ) -> dict:
        """
        Browse files and directories in a repository with token optimization.

        Args:
            repository: Repository identifier (PHID, callsign, or name)
            path: Path to browse (default: root "/")
            commit: Specific commit to browse (default: latest)
            max_tokens: Maximum token budget for response (default: 5000)

        Returns:
            List of files and directories at the specified path with pagination metadata
        """
        client = get_client_func()

        result = client.diffusion.browse_query(
            repository=repository,
            path=path if path else "/",
            commit=commit if commit else None,
        )

        # Apply token optimization to large browse results
        if max_tokens and result.get("data") and isinstance(result["data"], list):
            data = result["data"]
            if len(data) > 50:  # Limit directory listing for token optimization
                result["data"] = data[:50]
                result["token_optimization"] = {
                    "applied": True,
                    "original_count": len(data),
                    "returned_count": 50,
                    "reason": "Token budget optimization for directory listing",
                }

        # Add pagination metadata
        result = _add_pagination_metadata(result, result.get("cursor"))

        return {"success": True, "browse_result": result}

    @mcp.tool()
    @handle_api_errors
    def pha_repository_file_content(
        repository: str,
        file_path: str,
        commit: str = "",
    ) -> dict:
        """
        Get the content of a specific file from a repository.

        Args:
            repository: Repository identifier (PHID, callsign, or name)
            file_path: Path to the file
            commit: Specific commit (default: latest)

        Returns:
            File content and metadata
        """
        client = get_client_func()

        result = client.diffusion.file_content_query(
            repository=repository, path=file_path, commit=commit if commit else None
        )

        return {"success": True, "file_content": result}

    @mcp.tool()
    @handle_api_errors
    @optimize_token_usage
    def pha_repository_history(
        repository: str,
        path: str = "",
        commit: str = "",
        limit: int = 20,
        max_tokens: int = 5000,
    ) -> dict:
        """
        Get commit history for a repository or specific path with token optimization.

        Args:
            repository: Repository identifier (PHID, callsign, or name)
            path: Specific path to get history for (optional)
            commit: Starting commit (default: latest)
            limit: Maximum number of commits to return (default: 20, max: 100)
            max_tokens: Maximum token budget for response (default: 5000)

        Returns:
            Commit history with pagination metadata
        """
        client = get_client_func()

        result = client.diffusion.history_query(
            repository=repository,
            path=path if path else None,
            commit=commit if commit else None,
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

        return {"success": True, "history": result}

    @mcp.tool()
    @handle_api_errors
    def pha_repository_branches(repository: str) -> dict:
        """
        Get all branches in a repository.

        Args:
            repository: Repository identifier (PHID, callsign, or name)

        Returns:
            List of branches
        """
        client = get_client_func()

        result = client.diffusion.branch_query(repository=repository)

        return {"success": True, "branches": result}

    @mcp.tool()
    @handle_api_errors
    def pha_repository_commits_search(
        repository: str = "",
        author: str = "",
        message_contains: str = "",
        limit: int = 20,
    ) -> dict:
        """
        Search for commits across repositories.

        Args:
            repository: Repository identifier to search in (optional)
            author: Filter by commit author
            message_contains: Filter by commit message containing this text
            limit: Maximum number of results to return

        Returns:
            List of matching commits
        """
        client = get_client_func()

        constraints = {}
        if repository:
            constraints["repositories"] = [repository]
        if author:
            constraints["authors"] = [author]
        if message_contains:
            constraints["query"] = message_contains

        result = client.diffusion.search_commits(
            constraints=constraints if constraints else None, limit=limit
        )

        return {"success": True, "commits": result}

    # Differential (Code Review) Tools

    @mcp.tool()
    @handle_api_errors
    def pha_diff_create_from_content(
        diff_content: str,
        repository: str = "",
    ) -> dict:
        """
        Create a diff from raw diff content.

        Args:
            diff_content: Raw unified diff content
            repository: Repository identifier to associate with (optional)

        Returns:
            Created diff information
        """
        client = get_client_func()

        repository_phid = None
        if repository:
            # Try to resolve repository to PHID
            repos = client.diffusion.search_repositories(
                constraints=(
                    {"callsigns": [repository]}
                    if repository.isupper()
                    else {"names": [repository]}
                ),
                limit=1,
            )
            if repos.get("data"):
                repository_phid = repos["data"][0]["phid"]

        result = client.differential.create_raw_diff(
            diff=diff_content, repository_phid=repository_phid
        )

        return {"success": True, "diff": result}

    @mcp.tool()
    @handle_api_errors
    def pha_diff_create(
        diff_id: str,
        title: str,
        summary: str = "",
        test_plan: str = "",
        reviewers: List[str] = [],
    ) -> dict:
        """
        Create a new code review (Differential revision).

        Args:
            diff_id: ID or PHID of the diff to review
            title: Review title
            summary: Detailed description of the changes
            test_plan: How the changes were tested
            reviewers: List of reviewer usernames or PHIDs

        Returns:
            Created revision information
        """
        client = get_client_func()

        transactions = [
            {"type": "title", "value": title},
            {"type": "update", "value": diff_id},
        ]

        if summary:
            transactions.append({"type": "summary", "value": summary})
        if test_plan:
            transactions.append({"type": "testPlan", "value": test_plan})
        if reviewers:
            transactions.append({"type": "reviewers.add", "value": reviewers})

        result = client.differential.edit_revision(transactions=transactions)

        return {"success": True, "revision": result}

    @mcp.tool()
    @handle_api_errors
    @optimize_token_usage
    def pha_diff_search(
        author: str = "",
        reviewer: str = "",
        status: str = "",
        repository: str = "",
        title_contains: str = "",
        limit: int = 50,
        max_tokens: int = 5000,
    ) -> dict:
        """
        Search for code reviews (Differential revisions) with token optimization.

        Args:
            author: Filter by author username or PHID
            reviewer: Filter by reviewer username or PHID
            status: Filter by status ("open", "closed", "abandoned", "accepted")
            repository: Filter by repository name or PHID
            title_contains: Filter by title containing this text
            limit: Maximum number of results to return (default: 50, max: 500)
            max_tokens: Maximum token budget for response (default: 5000)

        Returns:
            List of matching code reviews with pagination metadata
        """
        client = get_client_func()

        constraints = {}
        if author:
            constraints["authorPHIDs"] = [author]
        if reviewer:
            constraints["reviewerPHIDs"] = [reviewer]
        if status:
            constraints["statuses"] = [status]
        if repository:
            constraints["repositoryPHIDs"] = [repository]
        if title_contains:
            constraints["query"] = title_contains

        result = client.differential.search_revisions(
            constraints=constraints if constraints else None, limit=limit
        )

        # Apply token optimization
        if max_tokens and result.get("data"):
            data = result["data"]
            if len(data) > 10:  # Further reduce limit for token optimization
                result["data"] = data[:10]
                result["token_optimization"] = {
                    "applied": True,
                    "original_count": len(data),
                    "returned_count": 10,
                    "reason": "Token budget optimization",
                }

        # Add pagination metadata
        result = _add_pagination_metadata(result, result.get("cursor"))

        return {"success": True, "revisions": result}

    @mcp.tool()
    @handle_api_errors
    def pha_diff_get(revision_id: str) -> dict:
        """
        Get detailed information about a specific code review.

        Args:
            revision_id: Revision ID (e.g., "D123") or PHID

        Returns:
            Detailed revision information
        """
        client = get_client_func()

        # Parse revision ID if in "D123" format
        if revision_id.startswith("D"):
            revision_id = revision_id[1:]

        result = client.differential.search_revisions(
            constraints={"ids": [int(revision_id)]}, limit=1
        )

        if result.get("data"):
            return {"success": True, "revision": result["data"][0]}
        else:
            return {"success": False, "error": f"Revision {revision_id} not found"}

    @mcp.tool()
    @handle_api_errors
    def pha_diff_add_comment(
        revision_id: str,
        comment: str,
        action: str = "comment",
    ) -> dict:
        """
        Add a comment to a code review.

        Args:
            revision_id: Revision ID (e.g., "D123") or PHID
            comment: Comment text
            action: Review action ("comment", "accept", "reject", "request-changes")

        Returns:
            Success status
        """
        client = get_client_func()

        transactions = [{"type": "comment", "value": comment}]

        if action == "accept":
            transactions.append({"type": "accept", "value": True})
        elif action == "reject":
            transactions.append({"type": "reject", "value": True})
        elif action == "request-changes":
            transactions.append({"type": "request-changes", "value": True})

        client.differential.edit_revision(
            transactions=transactions, object_identifier=revision_id
        )

        return {"success": True, "comment_added": True}

    @mcp.tool()
    @handle_api_errors
    def pha_diff_update(
        revision_id: str,
        new_diff_id: str = "",
        title: str = "",
        summary: str = "",
        test_plan: str = "",
        comment: str = "",
    ) -> dict:
        """
        Update an existing code review with new diff or metadata.

        Args:
            revision_id: Revision ID (e.g., "D123") or PHID
            new_diff_id: New diff ID or PHID to update the review with
            title: New title (optional)
            summary: New summary (optional)
            test_plan: New test plan (optional)
            comment: Comment explaining the update

        Returns:
            Updated revision information
        """
        client = get_client_func()

        transactions = []

        if new_diff_id:
            transactions.append({"type": "update", "value": new_diff_id})
        if title:
            transactions.append({"type": "title", "value": title})
        if summary:
            transactions.append({"type": "summary", "value": summary})
        if test_plan:
            transactions.append({"type": "testPlan", "value": test_plan})
        if comment:
            transactions.append({"type": "comment", "value": comment})

        if not transactions:
            return {"success": False, "error": "No updates specified"}

        result = client.differential.edit_revision(
            transactions=transactions, object_identifier=revision_id
        )

        return {"success": True, "revision": result}

    @mcp.tool()
    @handle_api_errors
    def pha_diff_get_content(diff_id: str) -> dict:
        """
        Get the raw content of a diff.

        Args:
            diff_id: Diff ID or PHID, you can use `search_diffds` with `D123` form id to get actual diff_id

        Returns:
            Raw diff content
        """
        client = get_client_func()

        # Parse diff ID if needed
        if diff_id.isdigit():
            diff_id = int(diff_id)

        result = client.differential.get_raw_diff(diff_id=diff_id)

        return {"success": True, "diff_content": result}

    @mcp.tool()
    @handle_api_errors
    def pha_diff_get_commit_message(revision_id: str) -> dict:
        """
        Get a commit message template for a code review.

        Args:
            revision_id: Revision ID (e.g., "D123") or PHID

        Returns:
            Formatted commit message template
        """
        client = get_client_func()

        # Parse revision ID if in "D123" format
        if revision_id.startswith("D"):
            revision_id = revision_id[1:]

        result = client.differential.get_commit_message(revision_id=int(revision_id))

        return {"success": True, "commit_message": result}

    # Project API Tools

    @mcp.tool()
    @handle_api_errors
    @optimize_token_usage
    def pha_project_search(
        query_key: str = "",
        ids: List[int] = [],
        phids: List[str] = [],
        names: List[str] = [],
        name_like: str = "",
        slugs: List[str] = [],
        ancestors: List[str] = [],
        descendants: List[str] = [],
        depth: int = None,
        status: str = "",
        is_milestone: bool = None,
        has_parent: bool = None,
        icon: str = "",
        color: str = "",
        limit: int = 100,
        max_tokens: int = 5000,
    ) -> dict:
        """
        Search for projects with advanced filtering capabilities and token optimization.

        Args:
            query_key: Builtin query ("active", "all", "archived")
            ids: List of specific project IDs to search for
            phids: List of specific project PHIDs to search for
            names: List of exact project names to find
            name_like: Find projects whose names contain this substring
            slugs: List of project slugs to find
            ancestors: Find projects with these ancestors (PHIDs)
            descendants: Find projects with these descendants (PHIDs)
            depth: Maximum depth to search for ancestors/descendants
            status: Filter by project status ("active", "archived")
            is_milestone: Filter for milestone projects
            has_parent: Filter for projects with/without parents
            icon: Filter by project icon
            color: Filter by project color
            limit: Maximum number of results to return (default: 100, max: 1000)
            max_tokens: Maximum token budget for response (default: 5000)

        Returns:
            Search results with project data, pagination metadata, and token optimization info
        """
        client = get_client_func()

        # Build constraints
        constraints = {}

        if ids:
            constraints["ids"] = ids
        if phids:
            constraints["phids"] = phids
        if names:
            constraints["names"] = names
        if name_like:
            constraints["nameLike"] = name_like
        if slugs:
            constraints["slugs"] = slugs
        if ancestors:
            constraints["ancestors"] = ancestors
        if descendants:
            constraints["descendants"] = descendants
        if depth is not None:
            constraints["depth"] = depth
        if status:
            constraints["status"] = status
        if is_milestone is not None:
            constraints["isMilestone"] = is_milestone
        if has_parent is not None:
            constraints["hasParent"] = has_parent
        if icon:
            constraints["icon"] = icon
        if color:
            constraints["color"] = color

        result = client.project.search_projects(
            constraints=constraints if constraints else None,
            limit=limit,
        )

        # Add pagination metadata
        result = _add_pagination_metadata(result, result.get("cursor"))

        return {"success": True, "projects": result}

    @mcp.tool()
    @handle_api_errors
    def pha_project_create(
        name: str,
        description: str = "",
        icon: str = "",
        color: str = "",
    ) -> dict:
        """
        Create a new project in Phabricator.

        Args:
            name: Project name (required)
            description: Project description
            icon: Project icon (e.g., "fa-briefcase", "fa-users")
            color: Project color (e.g., "red", "blue", "green")

        Returns:
            Created project information
        """
        client = get_client_func()

        result = client.project.create_project(
            name=name,
            description=description,
            icon=icon if icon else None,
            color=color if color else None,
        )

        return {"success": True, "project": result}

    @mcp.tool()
    @handle_api_errors
    def pha_project_get(project_identifier: str) -> dict:
        """
        Get detailed information about a specific project.

        Args:
            project_identifier: Project ID, PHID, name, or slug

        Returns:
            Project information
        """
        client = get_client_func()

        # Try different search strategies based on identifier format
        result = None

        # 1. If it looks like a PHID, search by PHID
        if project_identifier.startswith("PHID-PROJ-"):
            result = client.project.search_projects(
                constraints={"phids": [project_identifier]},
                limit=1,
            )

        # 2. If it's numeric, search by ID
        elif project_identifier.isdigit():
            result = client.project.search_projects(
                constraints={"ids": [int(project_identifier)]},
                limit=1,
            )

        # 3. Try searching by name or slug
        if not result or not result.get("data"):
            result = client.project.search_projects(
                constraints={"nameLike": project_identifier},
                limit=10,
            )
            # Filter for exact match
            if result.get("data"):
                exact_match = None
                for project in result["data"]:
                    fields = project.get("fields", {})
                    if (
                        fields.get("name") == project_identifier
                        or fields.get("slug") == project_identifier
                    ):
                        exact_match = project
                        break

                if exact_match:
                    result = {"data": [exact_match]}

        if result and result.get("data"):
            return {"success": True, "project": result["data"][0]}
        else:
            return {
                "success": False,
                "error": f"Project '{project_identifier}' not found",
            }

    @mcp.tool()
    @handle_api_errors
    def pha_project_update(
        project_phid: str,
        name: str = "",
        description: str = "",
        icon: str = "",
        color: str = "",
    ) -> dict:
        """
        Update an existing project in Phabricator.

        Args:
            project_phid: Project PHID to update
            name: New project name
            description: New project description
            icon: New project icon
            color: New project color

        Returns:
            Updated project information
        """
        client = get_client_func()

        # Build transactions
        transactions = []

        if name:
            transactions.append({"type": "name", "value": name})
        if description:
            transactions.append({"type": "description", "value": description})
        if icon:
            transactions.append({"type": "icon", "value": icon})
        if color:
            transactions.append({"type": "color", "value": color})

        if not transactions:
            return {"success": False, "error": "No updates specified"}

        result = client.project.edit_project(
            transactions=transactions,
            object_identifier=project_phid,
        )

        return {"success": True, "project": result}

    # Workboard Tools

    @mcp.tool()
    @handle_api_errors
    @optimize_token_usage
    def pha_workboard_search_columns(
        project_phids: List[str] = [],
        phids: List[str] = [],
        names: List[str] = [],
        is_hidden: bool = None,
        limit: int = 100,
        max_tokens: int = 5000,
    ) -> dict:
        """
        Search for workboard columns with filtering capabilities and token optimization.

        Args:
            project_phids: List of project PHIDs to search columns in
            phids: List of specific column PHIDs to search for
            names: List of column names to find
            is_hidden: Filter for hidden/visible columns
            limit: Maximum number of results to return (default: 100, max: 1000)
            max_tokens: Maximum token budget for response (default: 5000)

        Returns:
            Search results with column data, pagination metadata, and token optimization info
        """
        client = get_client_func()

        # Build constraints
        constraints = {}

        if project_phids:
            constraints["projects"] = project_phids
        if phids:
            constraints["phids"] = phids
        if names:
            constraints["names"] = names
        if is_hidden is not None:
            constraints["isHidden"] = is_hidden

        result = client.project.search_columns(
            constraints=constraints if constraints else None,
            limit=limit,
        )

        # Add pagination metadata
        result = _add_pagination_metadata(result, result.get("cursor"))

        return {"success": True, "columns": result}

    @mcp.tool()
    @handle_api_errors
    def pha_workboard_move_task(
        task_id: str,
        column_phid: str,
        before_phid: str = "",
        after_phid: str = "",
    ) -> dict:
        """
        Move a task to a specific workboard column with optional positioning.

        Args:
            task_id: Task ID or PHID to move
            column_phid: Target column PHID
            before_phid: Position before this task PHID (optional)
            after_phid: Position after this task PHID (optional)

        Returns:
            Success status and updated task information
        """
        client = get_client_func()

        # Create column transaction
        transaction = client.maniphest.create_column_transaction(
            column_phid=column_phid,
            before_phids=[before_phid] if before_phid else None,
            after_phids=[after_phid] if after_phid else None,
        )

        # Apply the transaction
        result = client.maniphest.edit_task(
            object_identifier=task_id,
            transactions=[transaction],
        )

        return {"success": True, "task": result}

    @mcp.tool()
    @handle_api_errors
    @optimize_token_usage
    def pha_workboard_search_tasks_by_column(
        column_phid: str,
        limit: int = 100,
        max_tokens: int = 5000,
    ) -> dict:
        """
        Search for tasks in a specific workboard column.

        Args:
            column_phid: Column PHID to search tasks in
            limit: Maximum number of results to return (default: 100, max: 1000)
            max_tokens: Maximum token budget for response (default: 5000)

        Returns:
            Search results with task data, pagination metadata, and token optimization info
        """
        client = get_client_func()

        # Build constraints for column search
        constraints = {
            "columnPHIDs": [column_phid],
        }

        result = client.maniphest.search_tasks(
            constraints=constraints,
            limit=limit,
        )

        # Add pagination metadata
        result = _add_pagination_metadata(result, result.get("cursor"))

        return {"success": True, "tasks": result}
