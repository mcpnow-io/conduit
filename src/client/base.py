import json
import urllib.parse
from abc import ABC
from typing import Any, Dict, Optional

import httpx


class PhabricatorAPIError(Exception):
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        error_info: Optional[str] = None,
    ):
        self.error_code = error_code
        self.error_info = error_info
        super().__init__(message)


class BasePhabricatorClient(ABC):
    def __init__(
        self, api_url: str, api_token: str, http_client: Optional[httpx.Client] = None
    ):
        """
        Initialize the base Phabricator client.

        Args:
            api_url: Base URL for the Phabricator API
            api_token: API token for authentication
            http_client: Optional httpx client to reuse
        """
        self.api_url = api_url.rstrip("/") + "/"
        self.api_token = api_token
        self._owns_client = http_client is None

        if http_client is None:
            self.client = httpx.Client(
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)",
                },
                timeout=30.0,
                follow_redirects=True,
            )
        else:
            self.client = http_client

    def _make_request(
        self, method: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the Phabricator API.

        Args:
            method: API method name (e.g., 'maniphest.search')
            params: Parameters to send with the request, every value is JSON formatted

        Returns:
            Response data from the API

        Raises:
            PhabricatorAPIError: If the API returns an error
            httpx.HTTPError: If there's a network error
        """
        if params is None:
            params = {}

        params["api.token"] = self.api_token

        url = urllib.parse.urljoin(self.api_url, method)

        try:
            response = self.client.post(url, data=params)
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

    def close(self):
        """Close the HTTP client if we own it."""
        if self._owns_client and self.client:
            self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
