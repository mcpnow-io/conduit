from typing import Any, Dict, List

from src.client.base import BasePhabricatorClient


class DiffusionClient(BasePhabricatorClient):
    def search_repositories(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Read information about repositories.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Repository search results
        """
        params = {"limit": limit}

        if constraints:
            flattened_constraints = dict(
                self.flatten_params(constraints, "constraints")
            )
            params.update(flattened_constraints)

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
        params = {}

        if object_identifier:
            params["objectIdentifier"] = object_identifier

        if transactions:
            params = {
                **{k: v for k, v in self.flatten_params(transactions, "transactions")},
                **params,
            }

        return self._make_request("diffusion.repository.edit", params)

    def create_repository(
        self,
        name: str,
        vcs_type: str = "git",
        callsign: str = None,
        short_name: str = None,
        description: str = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a new repository.

        Args:
            name: Repository name
            vcs_type: Version control system type (git, hg, svn)
            callsign: Repository callsign
            short_name: Short name for the repository
            description: Repository description
            **kwargs: Additional repository settings

        Returns:
            Created repository data
        """
        transactions = [
            {"type": "name", "value": name},
            {"type": "vcs", "value": vcs_type},
            {"type": "status", "value": "active"},
        ]

        if callsign:
            transactions.append({"type": "callsign", "value": callsign})
        if short_name:
            transactions.append({"type": "shortName", "value": short_name})
        if description:
            transactions.append({"type": "description", "value": description})

        # Add any additional settings
        for key, value in kwargs.items():
            transactions.append({"type": key, "value": value})

        return self.edit_repository(transactions)

    def search_commits(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Read information about commits.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Commit search results
        """
        params = {"limit": limit}

        if constraints:
            flattened_constraints = dict(
                self.flatten_params(constraints, "constraints")
            )
            params.update(flattened_constraints)

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
        params = {"objectIdentifier": object_identifier}

        if transactions:
            params = {
                **{k: v for k, v in self.flatten_params(transactions, "transactions")},
                **params,
            }

        return self._make_request("diffusion.commit.edit", params)

    def browse_query(
        self, repository: str, path: str = None, commit: str = None, **kwargs
    ) -> Dict[str, Any]:
        """
        File(s) information for a repository at an (optional) path and commit.

        Args:
            repository: Repository identifier (PHID, callsign, or short name)
            path: Path to browse
            commit: Commit identifier
            **kwargs: Additional query parameters

        Returns:
            Browse results
        """
        params = {"repository": repository}
        if path:
            params["path"] = path
        if commit:
            params["commit"] = commit

        params.update(kwargs)
        return self._make_request("diffusion.browsequery", params)

    def file_content_query(
        self, repository: str, path: str, commit: str = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Retrieve file content from a repository.

        Args:
            repository: Repository identifier
            path: File path
            commit: Commit identifier
            **kwargs: Additional query parameters

        Returns:
            File content data
        """
        params = {"repository": repository, "path": path}
        if commit:
            params["commit"] = commit

        params.update(kwargs)
        return self._make_request("diffusion.filecontentquery", params)

    def history_query(
        self,
        repository: str,
        path: str = None,
        commit: str = None,
        limit: int = 100,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Returns history information for a repository at a specific commit and path.

        Args:
            repository: Repository identifier
            path: Path to get history for
            commit: Commit identifier
            limit: Maximum number of results
            **kwargs: Additional query parameters

        Returns:
            History data
        """
        params = {"repository": repository, "limit": limit}
        if path:
            params["path"] = path
        if commit:
            params["commit"] = commit

        params.update(kwargs)
        return self._make_request("diffusion.historyquery", params)

    def raw_diff_query(
        self, repository: str, commit: str, path: str = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get raw diff information from a repository for a specific commit.

        Args:
            repository: Repository identifier
            commit: Commit identifier
            path: Optional path to limit diff to
            **kwargs: Additional query parameters

        Returns:
            Raw diff data
        """
        params = {"repository": repository, "commit": commit}
        if path:
            params["path"] = path

        params.update(kwargs)
        return self._make_request("diffusion.rawdiffquery", params)

    def branch_query(self, repository: str, **kwargs) -> Dict[str, Any]:
        """
        Determine what branches exist for a repository.

        Args:
            repository: Repository identifier
            **kwargs: Additional query parameters

        Returns:
            Branch information
        """
        params = {"repository": repository}
        params.update(kwargs)
        return self._make_request("diffusion.branchquery", params)

    def tags_query(self, repository: str, **kwargs) -> Dict[str, Any]:
        """
        Retrieve information about tags in a repository.

        Args:
            repository: Repository identifier
            **kwargs: Additional query parameters

        Returns:
            Tag information
        """
        params = {"repository": repository}
        params.update(kwargs)
        return self._make_request("diffusion.tagsquery", params)

    def resolve_refs(
        self, repository: str, refs: List[str], **kwargs
    ) -> Dict[str, Any]:
        """
        Resolve references into stable, canonical identifiers.

        Args:
            repository: Repository identifier
            refs: List of references to resolve
            **kwargs: Additional query parameters

        Returns:
            Resolved reference data
        """
        params = {"repository": repository, "refs": refs}
        params.update(kwargs)
        return self._make_request("diffusion.resolverefs", params)

    def search_query(
        self, repository: str, grep: str, path: str = None, commit: str = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Search (grep) a repository at a specific path and commit.

        Args:
            repository: Repository identifier
            grep: Search pattern
            path: Path to search in
            commit: Commit identifier
            **kwargs: Additional query parameters

        Returns:
            Search results
        """
        params = {"repository": repository, "grep": grep}
        if path:
            params["path"] = path
        if commit:
            params["commit"] = commit

        params.update(kwargs)
        return self._make_request("diffusion.searchquery", params)

    def blame_query(
        self, repository: str, paths: List[str], commit: str = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get blame information for a list of paths.

        Args:
            repository: Repository identifier
            paths: List of file paths
            commit: Commit identifier
            **kwargs: Additional query parameters

        Returns:
            Blame information
        """
        params = {"repository": repository, "paths": paths}
        if commit:
            params["commit"] = commit

        params.update(kwargs)
        return self._make_request("diffusion.blame", params)

    def commit_parents_query(
        self, repository: str, commit: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Get the commit identifiers for a commit's parent or parents.

        Args:
            repository: Repository identifier
            commit: Commit identifier
            **kwargs: Additional query parameters

        Returns:
            Parent commit information
        """
        params = {"repository": repository, "commit": commit}
        params.update(kwargs)
        return self._make_request("diffusion.commitparentsquery", params)

    def exists_query(
        self, repository: str, commit: str, path: str = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Determine if code exists in a version control system.

        Args:
            repository: Repository identifier
            commit: Commit identifier
            path: Path to check
            **kwargs: Additional query parameters

        Returns:
            Existence information
        """
        params = {"repository": repository, "commit": commit}
        if path:
            params["path"] = path

        params.update(kwargs)
        return self._make_request("diffusion.existsquery", params)
