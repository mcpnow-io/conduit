from typing import Any, Dict, List

from .base import BaseAsyncPhabricatorClient, BasePhabricatorClient


class DiffusionClient(BasePhabricatorClient):
    def search_repositories(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search for repositories.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Search results with repository data
        """
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints

        return self._make_request("diffusion.repository.search", params)

    def edit_repository(
        self, transactions: List[Dict[str, Any]], object_identifier: str = None
    ) -> Dict[str, Any]:
        """
        Apply transactions to create a new repository or edit an existing one.

        Args:
            transactions: List of transaction objects
            object_identifier: Existing repository identifier to update

        Returns:
            Repository data
        """
        params = {"transactions": transactions}
        if object_identifier:
            params["objectIdentifier"] = object_identifier

        return self._make_request("diffusion.repository.edit", params)

    def search_commits(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Read information about commits.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Commit information
        """
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints

        return self._make_request("diffusion.commit.search", params)

    def edit_commit(
        self, transactions: List[Dict[str, Any]], object_identifier: str
    ) -> Dict[str, Any]:
        """
        Apply transactions to edit an existing commit.

        Args:
            transactions: List of transaction objects
            object_identifier: Commit identifier

        Returns:
            Commit data
        """
        params = {"transactions": transactions, "objectIdentifier": object_identifier}

        return self._make_request("diffusion.commit.edit", params)

    def browse_repository(
        self, repository: str, path: str = "", commit: str = None
    ) -> Dict[str, Any]:
        """
        File(s) information for a repository at an (optional) path and (optional) commit.

        Args:
            repository: Repository identifier
            path: Path within repository
            commit: Commit identifier

        Returns:
            File/directory information
        """
        params = {"repository": repository, "path": path}
        if commit:
            params["commit"] = commit

        return self._make_request("diffusion.browsequery", params)

    def get_file_content(
        self, repository: str, path: str, commit: str = None
    ) -> Dict[str, Any]:
        """
        Retrieve file content from a repository.

        Args:
            repository: Repository identifier
            path: File path
            commit: Commit identifier

        Returns:
            File content
        """
        params = {"repository": repository, "path": path}
        if commit:
            params["commit"] = commit

        return self._make_request("diffusion.filecontentquery", params)

    def get_history(
        self, repository: str, path: str = "", commit: str = None, limit: int = 20
    ) -> Dict[str, Any]:
        """
        Returns history information for a repository at a specific commit and path.

        Args:
            repository: Repository identifier
            path: Path within repository
            commit: Commit identifier
            limit: Maximum number of commits to return

        Returns:
            History information
        """
        params = {"repository": repository, "path": path, "limit": limit}
        if commit:
            params["commit"] = commit

        return self._make_request("diffusion.historyquery", params)

    def get_blame(
        self, repository: str, paths: List[str], commit: str = None
    ) -> Dict[str, Any]:
        """
        Get blame information for a list of paths.

        Args:
            repository: Repository identifier
            paths: List of file paths
            commit: Commit identifier

        Returns:
            Blame information
        """
        params = {"repository": repository, "paths": paths}
        if commit:
            params["commit"] = commit

        return self._make_request("diffusion.blame", params)

    def get_branches(self, repository: str) -> Dict[str, Any]:
        """
        Determine what branches exist for a repository.

        Args:
            repository: Repository identifier

        Returns:
            Branch information
        """
        return self._make_request("diffusion.branchquery", {"repository": repository})

    def get_tags(self, repository: str, limit: int = 100) -> Dict[str, Any]:
        """
        Retrieve information about tags in a repository.

        Args:
            repository: Repository identifier
            limit: Maximum number of tags to return

        Returns:
            Tag information
        """
        return self._make_request(
            "diffusion.tagsquery", {"repository": repository, "limit": limit}
        )

    def get_diff(
        self, repository: str, path: str = "", commit: str = None
    ) -> Dict[str, Any]:
        """
        Get diff information from a repository for a specific path at an (optional) commit.

        Args:
            repository: Repository identifier
            path: Path within repository
            commit: Commit identifier

        Returns:
            Diff information
        """
        params = {"repository": repository, "path": path}
        if commit:
            params["commit"] = commit

        return self._make_request("diffusion.diffquery", params)

    def get_raw_diff(
        self, repository: str, commit: str, path: str = ""
    ) -> Dict[str, Any]:
        """
        Get raw diff information from a repository for a specific commit at an (optional) path.

        Args:
            repository: Repository identifier
            commit: Commit identifier
            path: Path within repository

        Returns:
            Raw diff information
        """
        params = {"repository": repository, "commit": commit}
        if path:
            params["path"] = path

        return self._make_request("diffusion.rawdiffquery", params)

    def search_files(
        self,
        repository: str,
        pattern: str,
        path: str = "",
        commit: str = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Filename search on a repository.

        Args:
            repository: Repository identifier
            pattern: Search pattern
            path: Path within repository to search
            commit: Commit identifier
            limit: Maximum number of results

        Returns:
            Search results
        """
        params = {"repository": repository, "pattern": pattern, "limit": limit}
        if path:
            params["path"] = path
        if commit:
            params["commit"] = commit

        return self._make_request("diffusion.querypaths", params)

    def search_content(
        self,
        repository: str,
        pattern: str,
        path: str = "",
        commit: str = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Search (grep) a repository at a specific path and commit.

        Args:
            repository: Repository identifier
            pattern: Search pattern (grep)
            path: Path within repository to search
            commit: Commit identifier
            limit: Maximum number of results

        Returns:
            Search results
        """
        params = {"repository": repository, "pattern": pattern, "limit": limit}
        if path:
            params["path"] = path
        if commit:
            params["commit"] = commit

        return self._make_request("diffusion.searchquery", params)

    def resolve_refs(self, repository: str, refs: List[str]) -> Dict[str, Any]:
        """
        Resolve references into stable, canonical identifiers.

        Args:
            repository: Repository identifier
            refs: List of references to resolve

        Returns:
            Resolved references
        """
        return self._make_request(
            "diffusion.resolverefs", {"repository": repository, "refs": refs}
        )

    def get_commit_parents(self, repository: str, commit: str) -> Dict[str, Any]:
        """
        Get the commit identifiers for a commit's parent or parents.

        Args:
            repository: Repository identifier
            commit: Commit identifier

        Returns:
            Parent commit information
        """
        return self._make_request(
            "diffusion.commitparentsquery", {"repository": repository, "commit": commit}
        )

    def get_merged_commits(
        self, repository: str, commit: str, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Merged commit information for a specific commit in a repository.

        Args:
            repository: Repository identifier
            commit: Commit identifier
            limit: Maximum number of commits to return

        Returns:
            Merged commit information
        """
        return self._make_request(
            "diffusion.mergedcommitsquery",
            {"repository": repository, "commit": commit, "limit": limit},
        )

    def get_last_modified(
        self, repository: str, paths: List[str], commit: str = None
    ) -> Dict[str, Any]:
        """
        Get the commits at which paths were last modified.

        Args:
            repository: Repository identifier
            paths: List of paths
            commit: Commit identifier

        Returns:
            Last modified information
        """
        params = {"repository": repository, "paths": paths}
        if commit:
            params["commit"] = commit

        return self._make_request("diffusion.lastmodifiedquery", params)

    def look_soon(self, repository: str) -> Dict[str, Any]:
        """
        Advise the server to look for new commits in a repository as soon as possible.

        Args:
            repository: Repository identifier

        Returns:
            Result
        """
        return self._make_request("diffusion.looksoon", {"repository": repository})


class AsyncDiffusionClient(BaseAsyncPhabricatorClient):
    """
    Async client for Diffusion (Repository) API operations.
    """

    async def search_repositories(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """Search for repositories asynchronously."""
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints
        return await self._make_request("diffusion.repository.search", params)

    async def browse_repository(
        self, repository: str, path: str = "", commit: str = None
    ) -> Dict[str, Any]:
        """Browse repository asynchronously."""
        params = {"repository": repository, "path": path}
        if commit:
            params["commit"] = commit
        return await self._make_request("diffusion.browsequery", params)

    async def get_file_content(
        self, repository: str, path: str, commit: str = None
    ) -> Dict[str, Any]:
        """Get file content asynchronously."""
        params = {"repository": repository, "path": path}
        if commit:
            params["commit"] = commit
        return await self._make_request("diffusion.filecontentquery", params)
