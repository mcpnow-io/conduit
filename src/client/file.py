"""
File management API client.
"""

from typing import Any, Dict

from .base import BaseAsyncPhabricatorClient, BasePhabricatorClient, PhabricatorAPIError


class FileClient(BasePhabricatorClient):
    """
    Client for File management API operations.

    Handles file upload, download, search, and other file operations.
    """

    def search_files(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Read information about files.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Search results with file data
        """
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints

        return self._make_request("file.search", params)

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

    def allocate_file(
        self, name: str, length: int, content_hash: str = None
    ) -> Dict[str, Any]:
        """
        Prepare to upload a file.

        Args:
            name: File name
            length: File length in bytes
            content_hash: Optional content hash

        Returns:
            Allocation information
        """
        params = {"name": name, "contentLength": length}
        if content_hash:
            params["contentHash"] = content_hash

        return self._make_request("file.allocate", params)

    def upload_file(self, data: bytes, name: str = None) -> Dict[str, Any]:
        """
        Upload a file to the server.

        Args:
            data: File data
            name: Optional file name

        Returns:
            Upload result
        """
        params = {"data_base64": data}
        if name:
            params["name"] = name

        return self._make_request("file.upload", params)

    def upload_chunk(
        self, file_phid: str, byte_start: int, data: bytes
    ) -> Dict[str, Any]:
        """
        Upload a chunk of file data to the server.

        Args:
            file_phid: File PHID
            byte_start: Starting byte position
            data: Chunk data

        Returns:
            Upload result
        """
        return self._make_request(
            "file.uploadchunk",
            {"filePHID": file_phid, "byteStart": byte_start, "data": data},
        )

    def query_chunks(self, file_phid: str) -> Dict[str, Any]:
        """
        Get information about file chunks.

        Args:
            file_phid: File PHID

        Returns:
            Chunk information
        """
        return self._make_request("file.querychunks", {"filePHID": file_phid})

    def download_file(self, file_phid: str) -> Dict[str, Any]:
        """
        Download a file from the server.

        Args:
            file_phid: File PHID

        Returns:
            File data
        """
        return self._make_request("file.download", {"phid": file_phid})

    def get_file_info_legacy(
        self, file_id: int = None, file_phid: str = None
    ) -> Dict[str, Any]:
        """
        Get information about a file (legacy method).

        Args:
            file_id: File ID
            file_phid: File PHID

        Returns:
            File information
        """
        params = {}
        if file_id:
            params["id"] = file_id
        if file_phid:
            params["phid"] = file_phid

        return self._make_request("file.info", params)


class AsyncFileClient(BaseAsyncPhabricatorClient):
    """
    Async client for File management API operations.
    """

    async def search_files(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """Search for files asynchronously."""
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints
        return await self._make_request("file.search", params)

    async def get_file_info(self, file_phid: str) -> Dict[str, Any]:
        """Get file information asynchronously."""
        params = {"constraints": {"phids": [file_phid]}}

        result = await self._make_request("file.search", params)

        if result.get("data"):
            return result["data"][0]
        else:
            raise PhabricatorAPIError(f"File {file_phid} not found")

    async def upload_file(self, data: bytes, name: str = None) -> Dict[str, Any]:
        """Upload a file asynchronously."""
        params = {"data_base64": data}
        if name:
            params["name"] = name
        return await self._make_request("file.upload", params)
