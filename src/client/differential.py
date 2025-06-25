from typing import Any, Dict, List

from .base import BasePhabricatorClient


class DifferentialClient(BasePhabricatorClient):
    def search_revisions(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search for Differential revisions.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Search results with revision data
        """
        params = {"limit": limit}

        if constraints:
            params["constraints"] = constraints

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
        params = {"transactions": transactions}
        if object_identifier:
            params["objectIdentifier"] = object_identifier

        return self._make_request("differential.revision.edit", params)

    def search_diffs(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Read information about diffs.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Diff information
        """
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints

        return self._make_request("differential.diff.search", params)

    def search_changesets(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Read information about changesets.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Changeset information
        """
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints

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
            "changes": changes,
            "sourceControlSystem": source_control_system,
            "sourceControlPath": source_control_path,
        }

        if source_control_base_revision:
            params["sourceControlBaseRevision"] = source_control_base_revision

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
