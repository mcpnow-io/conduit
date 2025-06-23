import json
import urllib.parse
from typing import Any, Dict, List, Optional

import httpx


class PhabricatorAPIError(Exception):
    """Exception raised for Phabricator API errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        error_info: Optional[str] = None,
    ):
        self.error_code = error_code
        self.error_info = error_info
        super().__init__(message)


class PhabricatorClient(object):
    """
    Client for interacting with Phabricator/Phorge Conduit API.

    This client handles authentication, request formatting, and response parsing
    for Phabricator API calls. Uses httpx for modern HTTP support including HTTP/2.
    """

    def __init__(self, api_url: str, api_token: str):
        """
        Initialize the Phabricator client.

        Args:
            api_url: Base URL for the Phabricator API (e.g., https://example.com/api/)
            api_token: API token for authentication
        """
        self.api_url = api_url.rstrip("/") + "/"
        self.api_token = api_token

        # Create httpx client with default configuration
        self.client = httpx.Client(
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)",
            },
            timeout=30.0,
            follow_redirects=True,
        )

    def _make_request(
        self, method: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the Phabricator API.

        Args:
            method: API method name (e.g., 'maniphest.search')
            params: Parameters to send with the request

        Returns:
            Response data from the API

        Raises:
            PhabricatorAPIError: If the API returns an error
            httpx.HTTPError: If there's a network error
        """
        if params is None:
            params = {}

        # Add API token to params
        params["api.token"] = self.api_token

        # Build the URL
        url = urllib.parse.urljoin(self.api_url, method)

        try:
            # Make the request
            response = self.client.post(url, data=params)
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Check for API errors
            if data.get("error_code"):
                raise PhabricatorAPIError(
                    message=f"API Error: {data.get('error_info', 'Unknown error')}",
                    error_code=data.get("error_code"),
                    error_info=data.get("error_info"),
                )

            return data.get("result", {})

        except httpx.HTTPError as e:
            raise PhabricatorAPIError(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            raise PhabricatorAPIError(f"Invalid JSON response: {str(e)}")

    def test_connection(self) -> Dict[str, Any]:
        """
        Test the API connection by calling user.whoami.

        Returns:
            User information if successful
        """
        return self._make_request("user.whoami")

    def search_tasks(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search for Maniphest tasks.

        Args:
            constraints: Search constraints (e.g., {'statuses': ['open']})
            limit: Maximum number of results to return

        Returns:
            Search results with task data
        """
        params = {"limit": limit}

        if constraints:
            params["constraints"] = constraints

        return self._make_request("maniphest.search", params)

    def get_task(self, task_id: int) -> Dict[str, Any]:
        """
        Get a specific task by ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            Task data
        """
        constraints = {"ids": [task_id]}
        result = self.search_tasks(constraints=constraints, limit=1)

        if result.get("data"):
            return result["data"][0]
        else:
            raise PhabricatorAPIError(f"Task {task_id} not found")

    def create_task(
        self,
        title: str,
        description: str = "",
        owner_phid: str = None,
        project_phids: List[str] = None,
        priority: str = None,
    ) -> Dict[str, Any]:
        """
        Create a new Maniphest task.

        Args:
            title: Task title
            description: Task description
            owner_phid: PHID of the task owner
            project_phids: List of project PHIDs to associate with the task
            priority: Task priority ('unbreak', 'high', 'normal', 'low', 'wish')

        Returns:
            Created task data
        """
        transactions = [{"type": "title", "value": title}]

        if description:
            transactions.append({"type": "description", "value": description})

        if owner_phid:
            transactions.append({"type": "owner", "value": owner_phid})

        if project_phids:
            transactions.append({"type": "projects.set", "value": project_phids})

        if priority:
            transactions.append({"type": "priority", "value": priority})

        params = {"transactions": transactions}

        return self._make_request("maniphest.edit", params)

    def update_task(
        self, task_id: int, transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update an existing task.

        Args:
            task_id: ID of the task to update
            transactions: List of transaction objects

        Returns:
            Updated task data
        """
        params = {"objectIdentifier": task_id, "transactions": transactions}

        return self._make_request("maniphest.edit", params)

    def search_projects(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search for projects.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Search results with project data
        """
        params = {"limit": limit}

        if constraints:
            params["constraints"] = constraints

        return self._make_request("project.search", params)

    def search_users(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search for users.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Search results with user data
        """
        params = {"limit": limit}

        if constraints:
            params["constraints"] = constraints

        return self._make_request("user.search", params)

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

    def get_file_info(self, file_phid: str) -> Dict[str, Any]:
        """
        Get information about a file.

        Args:
            file_phid: PHID of the file

        Returns:
            File information
        """
        params = {"constraints": {"phids": [file_phid]}}

        result = self._make_request("file.search", params)

        if result.get("data"):
            return result["data"][0]
        else:
            raise PhabricatorAPIError(f"File {file_phid} not found")

    def close(self):
        """Close the HTTP client."""
        if self.client:
            self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class AsyncPhabricatorClient:
    """
    Async version of PhabricatorClient for high-performance scenarios.
    """

    def __init__(self, api_url: str, api_token: str):
        """
        Initialize the async Phabricator client.

        Args:
            api_url: Base URL for the Phabricator API
            api_token: API token for authentication
        """
        self.api_url = api_url.rstrip("/") + "/"
        self.api_token = api_token

        # Create async httpx client
        self.client = httpx.AsyncClient(
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)",
            },
            timeout=30.0,
            follow_redirects=True,
        )

    async def _make_request(
        self, method: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make an async request to the Phabricator API.
        """
        if params is None:
            params = {}

        params["api.token"] = self.api_token
        url = urllib.parse.urljoin(self.api_url, method)

        try:
            response = await self.client.post(url, data=params)
            response.raise_for_status()

            data = response.json()

            if data.get("error_code"):
                raise PhabricatorAPIError(
                    message=f"API Error: {data.get('error_info', 'Unknown error')}",
                    error_code=data.get("error_code"),
                    error_info=data.get("error_info"),
                )

            return data.get("result", {})

        except httpx.HTTPError as e:
            raise PhabricatorAPIError(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            raise PhabricatorAPIError(f"Invalid JSON response: {str(e)}")

    async def test_connection(self) -> Dict[str, Any]:
        """Test the API connection asynchronously."""
        return await self._make_request("user.whoami")

    async def search_tasks(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """Search for tasks asynchronously."""
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints
        return await self._make_request("maniphest.search", params)

    async def create_task(
        self,
        title: str,
        description: str = "",
        owner_phid: str = None,
        project_phids: List[str] = None,
        priority: str = None,
    ) -> Dict[str, Any]:
        """Create a task asynchronously."""
        transactions = [{"type": "title", "value": title}]

        if description:
            transactions.append({"type": "description", "value": description})
        if owner_phid:
            transactions.append({"type": "owner", "value": owner_phid})
        if project_phids:
            transactions.append({"type": "projects.set", "value": project_phids})
        if priority:
            transactions.append({"type": "priority", "value": priority})

        params = {"transactions": transactions}
        return await self._make_request("maniphest.edit", params)

    async def close(self):
        """Close the async HTTP client."""
        if self.client:
            await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
