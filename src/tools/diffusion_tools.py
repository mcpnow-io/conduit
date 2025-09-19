from fastmcp import FastMCP

from src.tools.handlers import handle_api_errors
from src.tools.pagination import _add_pagination_metadata


def register_diffusion_tools(
    mcp: FastMCP,
    get_client_func: callable,
    enable_type_safety: bool = False,
) -> None:
    """Register diffusion (repository) MCP tools."""

    @mcp.tool()
    @handle_api_errors
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
