from typing import Any, Dict, List

from src.client.base import BasePhabricatorClient
from src.utils import (
    build_search_params,
    build_transaction_params,
    flatten_params,
)


class DifferentialClient(BasePhabricatorClient):
    def search_revisions(
        self,
        query_key: str = None,
        constraints: Dict[str, Any] = None,
        attachments: Dict[str, bool] = None,
        order: str = None,
        before: str = None,
        after: str = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Search for Differential revisions using the modern search API.

        Args:
            query_key: Builtin query key (e.g., "active", "all", "authored", "active-drafts", etc.)
            constraints: Search constraints (e.g., {'ids': [123], 'authorPHIDs': ['PHID-...'], 'statuses': ['accepted']})
            attachments: Additional data to include in results
            order: Result ordering (builtin key or custom column list)
            before: Cursor for previous page
            after: Cursor for next page
            limit: Maximum number of results to return (default: 100)

        Returns:
            Search results with revision data, cursor info, and attachments
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
        return self._make_request("differential.revision.search", params)

    def edit_revision(
        self, transactions: List[Dict[str, Any]], object_identifier: str = None
    ) -> Dict[str, Any]:
        """
        Apply transactions to create or update a revision.

        Args:
            transactions: List of transaction objects
            object_identifier: Existing revision identifier to update

        Returns:
            Revision data
        """
        params = build_transaction_params(
            transactions=transactions,
            object_identifier=object_identifier,
        )
        return self._make_request("differential.revision.edit", params)

    def search_diffs(
        self,
        query_key: str = None,
        constraints: Dict[str, Any] = None,
        attachments: Dict[str, bool] = None,
        order: str = None,
        before: str = None,
        after: str = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Search for Differential diffs using the modern search API.

        Args:
            query_key: Builtin query key ("all")
            constraints: Search constraints (e.g., {'ids': [123], 'phids': ['PHID-...'], 'revisionPHIDs': ['PHID-...']})
            attachments: Additional data to include in results (e.g., {'commits': True})
            order: Result ordering ("newest", "oldest" or custom column list)
            before: Cursor for previous page
            after: Cursor for next page
            limit: Maximum number of results to return (default: 100)

        Returns:
            Search results with diff data, cursor info, and attachments
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
        return self._make_request("differential.diff.search", params)

    def search_changesets(
        self,
        query_key: str = None,
        constraints: Dict[str, Any] = None,
        attachments: Dict[str, bool] = None,
        order: str = None,
        before: str = None,
        after: str = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Search for Differential changesets using the modern search API.

        Args:
            query_key: Builtin query key
            constraints: Search constraints (e.g., {'diffPHIDs': ['PHID-...']})
            attachments: Additional data to include in results
            order: Result ordering (builtin key or custom column list)
            before: Cursor for previous page
            after: Cursor for next page
            limit: Maximum number of results to return (default: 100)

        Returns:
            Search results with changeset data, cursor info, and attachments
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
        return self._make_request("differential.changeset.search", params)

    def create_diff(
        self,
        changes: List[Dict[str, Any]],
        source_control_system: str = "git",
        source_control_path: str = "/",
        source_control_base_revision: str = None,
    ) -> Dict[str, Any]:
        """
        Create a new Differential diff.

        Args:
            changes: List of file changes
            source_control_system: Source control system (git, svn, hg, etc.)
            source_control_path: Base path in repository
            source_control_base_revision: Base revision

        Returns:
            Created diff data
        """
        params = {
            "sourceControlSystem": source_control_system,
            "sourceControlPath": source_control_path,
        }

        if source_control_base_revision:
            params["sourceControlBaseRevision"] = source_control_base_revision

        # Flatten changes properly
        if changes:
            flattened_changes = dict(flatten_params(changes, "changes"))
            params.update(flattened_changes)

        return self._make_request("differential.creatediff", params)

    def create_raw_diff(self, diff: str, repository_phid: str = None) -> Dict[str, Any]:
        """
        Create a new Differential diff from a raw diff source.

        Args:
            diff: Raw diff content
            repository_phid: Repository PHID

        Returns:
            Created diff data
        """
        params = {"diff": diff}
        if repository_phid:
            params["repositoryPHID"] = repository_phid

        return self._make_request("differential.createrawdiff", params)

    def get_raw_diff(self, diff_id: int) -> str:
        """
        Retrieve a raw diff.

        Args:
            diff_id: Diff ID

        Returns:
            Raw diff content
        """
        result = self._make_request("differential.getrawdiff", {"diffID": diff_id})
        return result

    def get_commit_message(
        self, revision_id: int = None, diff_id: int = None
    ) -> Dict[str, Any]:
        """
        Retrieve Differential commit messages or message templates.

        Args:
            revision_id: Revision ID
            diff_id: Diff ID

        Returns:
            Commit message information
        """
        params = {}
        if revision_id:
            params["revision_id"] = revision_id
        if diff_id:
            params["diff_id"] = diff_id

        return self._make_request("differential.getcommitmessage", params)

    def get_commit_paths(self, revision_id: int) -> List[str]:
        """
        Query which paths should be included when committing a revision.

        Args:
            revision_id: Revision ID

        Returns:
            List of paths
        """
        result = self._make_request(
            "differential.getcommitpaths", {"revision_id": revision_id}
        )
        return result

    def parse_commit_message(self, corpus: str) -> Dict[str, Any]:
        """
        Parse commit messages for Differential fields.

        Args:
            corpus: Commit message text

        Returns:
            Parsed fields
        """
        return self._make_request("differential.parsecommitmessage", {"corpus": corpus})

    def set_diff_property(self, diff_id: int, name: str, data: Any) -> Dict[str, Any]:
        """
        Attach properties to Differential diffs.

        Args:
            diff_id: Diff ID
            name: Property name
            data: Property data

        Returns:
            Result
        """
        return self._make_request(
            "differential.setdiffproperty",
            {"diff_id": diff_id, "name": name, "data": data},
        )

    def add_comment(
        self, revision_id: int, message: str = "", action: str = "comment"
    ) -> Dict[str, Any]:
        """
        Add a comment to a Differential revision (legacy method).

        Args:
            revision_id: Revision ID
            message: Comment message
            action: Action to take

        Returns:
            Comment data
        """
        return self._make_request(
            "differential.createcomment",
            {"revision_id": revision_id, "message": message, "action": action},
        )

    def add_inline_comment(
        self,
        revision_id: int,
        file_path: str,
        line_number: int,
        content: str,
        is_new: bool = True,
    ) -> Dict[str, Any]:
        """
        Add an inline comment to a Differential revision.

        Args:
            revision_id: Revision ID
            file_path: Path to the file
            line_number: Line number
            content: Comment content
            is_new: Whether this is for the new version of the file

        Returns:
            Inline comment data
        """
        return self._make_request(
            "differential.createinline",
            {
                "revisionID": revision_id,
                "filePath": file_path,
                "lineNumber": line_number,
                "content": content,
                "isNewFile": is_new,
            },
        )

    def close_revision(self, revision_id: int) -> Dict[str, Any]:
        """
        Close a Differential revision (legacy method).

        Args:
            revision_id: Revision ID

        Returns:
            Result
        """
        return self._make_request("differential.close", {"revisionID": revision_id})

    def query_revisions(
        self,
        ids: List[int] = None,
        phids: List[str] = None,
        authors: List[str] = None,
        reviewers: List[str] = None,
        paths: List[str] = None,
        commit_hashes: List[str] = None,
        status: str = None,
        order: str = None,
        limit: int = None,
        offset: int = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Query Differential revisions which match certain criteria (legacy method).

        Args:
            ids: List of revision IDs
            phids: List of revision PHIDs
            authors: List of author PHIDs
            reviewers: List of reviewer PHIDs
            paths: List of paths
            commit_hashes: List of commit hashes
            status: Status filter
            order: Order by field
            limit: Maximum results
            offset: Result offset
            **kwargs: Additional query parameters

        Returns:
            Query results
        """
        params = {}

        if ids:
            params["ids"] = ids
        if phids:
            params["phids"] = phids
        if authors:
            params["authors"] = authors
        if reviewers:
            params["reviewers"] = reviewers
        if paths:
            params["paths"] = paths
        if commit_hashes:
            params["commitHashes"] = commit_hashes
        if status:
            params["status"] = status
        if order:
            params["order"] = order
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset

        params.update(kwargs)
        return self._make_request("differential.query", params)

    def query_diffs(
        self,
        ids: List[int] = None,
        phids: List[str] = None,
        revision_ids: List[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Query differential diffs which match certain criteria (legacy method).

        Args:
            ids: List of diff IDs
            phids: List of diff PHIDs
            revision_ids: List of revision IDs
            **kwargs: Additional query parameters

        Returns:
            Query results
        """
        params = {}

        if ids:
            params["ids"] = ids
        if phids:
            params["phids"] = phids
        if revision_ids:
            params["revisionIDs"] = revision_ids

        params.update(kwargs)
        return self._make_request("differential.querydiffs", params)

    def update_revision(
        self, revision_id: int, diff_id: int = None, message: str = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Update a Differential revision (legacy method).

        Args:
            revision_id: Revision ID to update
            diff_id: New diff ID
            message: Update message
            **kwargs: Additional update parameters

        Returns:
            Update result
        """
        params = {"id": revision_id}

        if diff_id:
            params["diffid"] = diff_id
        if message:
            params["message"] = message

        params.update(kwargs)
        return self._make_request("differential.updaterevision", params)

    def create_revision(
        self,
        diff_id: int,
        title: str,
        summary: str = None,
        test_plan: str = None,
        reviewers: List[str] = None,
        cc: List[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a new Differential revision (legacy method).

        Args:
            diff_id: Diff ID
            title: Revision title
            summary: Revision summary
            test_plan: Test plan
            reviewers: List of reviewer PHIDs
            cc: List of CC PHIDs
            **kwargs: Additional creation parameters

        Returns:
            Created revision data
        """
        params = {"diffid": diff_id, "title": title}

        if summary:
            params["summary"] = summary
        if test_plan:
            params["testPlan"] = test_plan
        if reviewers:
            params["reviewerPHIDs"] = reviewers
        if cc:
            params["ccPHIDs"] = cc

        params.update(kwargs)
        return self._make_request("differential.createrevision", params)
