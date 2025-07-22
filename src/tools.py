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
    UserSearchAttachments,
    UserSearchConstraints,
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
    def search_users(
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
    ) -> dict:
        """
        Search for users with advanced filtering capabilities.

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
            limit: Maximum number of results to return (default: 100)

        Returns:
            Search results with user data and metadata
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

        # Call the search API
        result = client.user.search(
            query_key=query_key or None,
            constraints=constraints if constraints else None,
            attachments=attachments if attachments else None,
            order=order or None,
            limit=limit,
        )

        return {"success": True, "users": result["data"], "cursor": result["cursor"]}

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
            task_id: The ID of the task to retrieve, e.g. 1234

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

    # Diffusion (Repository) Tools

    @mcp.tool()
    @handle_api_errors
    def search_repositories(
        name_contains: str = "",
        vcs_type: str = "",
        status: str = "",
        limit: int = 50,
    ) -> dict:
        """
        Search for repositories in Phabricator.

        Args:
            name_contains: Filter repositories by name containing this string
            vcs_type: Filter by version control system ("git", "hg", "svn")
            status: Filter by repository status ("active", "inactive")
            limit: Maximum number of results to return

        Returns:
            List of repositories matching the criteria
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

        return {"success": True, "repositories": result}

    @mcp.tool()
    @handle_api_errors
    def create_repository(
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
    def get_repository_info(repository_identifier: str) -> dict:
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
    def browse_repository_files(
        repository: str,
        path: str = "/",
        commit: str = "",
    ) -> dict:
        """
        Browse files and directories in a repository.

        Args:
            repository: Repository identifier (PHID, callsign, or name)
            path: Path to browse (default: root "/")
            commit: Specific commit to browse (default: latest)

        Returns:
            List of files and directories at the specified path
        """
        client = get_client_func()

        result = client.diffusion.browse_query(
            repository=repository,
            path=path if path else "/",
            commit=commit if commit else None,
        )

        return {"success": True, "browse_result": result}

    @mcp.tool()
    @handle_api_errors
    def get_file_content(
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
    def get_repository_history(
        repository: str,
        path: str = "",
        commit: str = "",
        limit: int = 20,
    ) -> dict:
        """
        Get commit history for a repository or specific path.

        Args:
            repository: Repository identifier (PHID, callsign, or name)
            path: Specific path to get history for (optional)
            commit: Starting commit (default: latest)
            limit: Maximum number of commits to return

        Returns:
            Commit history
        """
        client = get_client_func()

        result = client.diffusion.history_query(
            repository=repository,
            path=path if path else None,
            commit=commit if commit else None,
            limit=limit,
        )

        return {"success": True, "history": result}

    @mcp.tool()
    @handle_api_errors
    def get_repository_branches(repository: str) -> dict:
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
    def search_repository_commits(
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
    def create_diff_from_content(
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
    def create_code_review(
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
    def search_code_reviews(
        author: str = "",
        reviewer: str = "",
        status: str = "",
        repository: str = "",
        title_contains: str = "",
        limit: int = 50,
    ) -> dict:
        """
        Search for code reviews (Differential revisions).

        Args:
            author: Filter by author username or PHID
            reviewer: Filter by reviewer username or PHID
            status: Filter by status ("open", "closed", "abandoned", "accepted")
            repository: Filter by repository name or PHID
            title_contains: Filter by title containing this text
            limit: Maximum number of results to return

        Returns:
            List of matching code reviews
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

        return {"success": True, "revisions": result}

    @mcp.tool()
    @handle_api_errors
    def get_code_review_details(revision_id: str) -> dict:
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
    def add_review_comment(
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
    def update_code_review(
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
    def get_diff_content(diff_id: str) -> dict:
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
    def search_diffs(
        revision_id: str = "",
        repository: str = "",
        author: str = "",
        limit: int = 20,
    ) -> dict:
        """
        Search for diffs in the system.

        Args:
            revision_id: Filter by specific revision ID
            repository: Filter by repository name or PHID
            author: Filter by author username or PHID
            limit: Maximum number of results to return

        Returns:
            List of matching diffs
        """
        client = get_client_func()

        constraints = {}
        if revision_id:
            # Convert revision ID to PHID for search
            if revision_id.startswith("D"):
                revision_id = revision_id[1:]

            # First, search for the revision to get its PHID
            revision_search = client.differential.search_revisions(
                constraints={"ids": [int(revision_id)]}, limit=1
            )

            if revision_search.get("data"):
                revision_phid = revision_search["data"][0]["phid"]
                constraints["revisionPHIDs"] = [revision_phid]
            else:
                # Return empty result if revision not found
                return {"success": True, "diffs": {"data": [], "cursor": {}}}

        if repository:
            constraints["repositories"] = [repository]
        if author:
            constraints["authors"] = [author]

        result = client.differential.search_diffs(
            constraints=constraints if constraints else None, limit=limit
        )

        return {"success": True, "diffs": result}

    @mcp.tool()
    @handle_api_errors
    def get_commit_message_template(revision_id: str) -> dict:
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
