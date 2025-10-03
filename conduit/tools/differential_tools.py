from typing import List, Optional

from fastmcp import FastMCP

from conduit.tools.handlers import handle_api_errors
from conduit.tools.pagination import _add_pagination_metadata


def register_differential_tools(
    mcp: FastMCP,
    get_client_func: callable,
    enable_type_safety: bool = False,
) -> None:
    """Register differential (code review) MCP tools."""

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
        reviewers: Optional[List[str]] = None,
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
        # Initialize None parameters to empty lists
        if reviewers is None:
            reviewers = []

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
