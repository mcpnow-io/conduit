"""Tests for file client."""

import pytest
from unittest.mock import patch

from conduit.client.file import FileClient
from conduit.client.base import PhabricatorAPIError


class TestFileClient:
    """Test FileClient methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = FileClient(
            api_url="http://test.example.com/api/", api_token="test_token"
        )

    @patch("src.client.base.BasePhabricatorClient._make_request")
    def test_search_files_success(self, mock_request):
        """Test successful file search."""
        mock_request.return_value = {
            "data": [
                {"phid": "PHID-FILE-1", "name": "test.txt"},
                {"phid": "PHID-FILE-2", "name": "example.pdf"},
            ]
        }

        result = self.client.search_files(constraints={"name": "test"}, limit=10)

        mock_request.assert_called_once_with(
            "file.search",
            {
                "constraints[name]": "test",
                "limit": 10,
            },
        )
        assert result["data"][0]["name"] == "test.txt"

    @patch("src.client.base.BasePhabricatorClient._make_request")
    def test_search_files_no_constraints(self, mock_request):
        """Test file search without constraints."""
        mock_request.return_value = {"data": []}

        result = self.client.search_files()

        mock_request.assert_called_once_with(
            "file.search",
            {
                "limit": 100,
            },
        )
        assert result["data"] == []

    @patch("src.client.base.BasePhabricatorClient._make_request")
    def test_get_file_info_success(self, mock_request):
        """Test successful file info retrieval."""
        mock_request.return_value = {
            "data": [
                {
                    "phid": "PHID-FILE-1",
                    "name": "test.txt",
                    "size": 1024,
                    "mimeType": "text/plain",
                }
            ]
        }

        result = self.client.get_file_info("PHID-FILE-1")

        mock_request.assert_called_once_with(
            "file.search",
            {
                "constraints": {"phids": ["PHID-FILE-1"]},
            },
        )
        assert result["name"] == "test.txt"
        assert result["size"] == 1024

    @patch("src.client.base.BasePhabricatorClient._make_request")
    def test_get_file_info_not_found(self, mock_request):
        """Test file info retrieval when file not found."""
        mock_request.return_value = {"data": []}

        with pytest.raises(PhabricatorAPIError) as exc_info:
            self.client.get_file_info("PHID-NONEXISTENT")

        assert "PHID-NONEXISTENT not found" in str(exc_info.value)

    @patch("src.client.base.BasePhabricatorClient._make_request")
    def test_allocate_file_success(self, mock_request):
        """Test successful file allocation."""
        mock_request.return_value = {
            "filePHID": "PHID-FILE-1",
            "uploadURI": "http://example.com/upload",
        }

        result = self.client.allocate_file(
            name="test.txt", length=1024, content_hash="abc123"
        )

        mock_request.assert_called_once_with(
            "file.allocate",
            {
                "name": "test.txt",
                "contentLength": 1024,
                "contentHash": "abc123",
            },
        )
        assert result["filePHID"] == "PHID-FILE-1"

    @patch("src.client.base.BasePhabricatorClient._make_request")
    def test_allocate_file_without_hash(self, mock_request):
        """Test file allocation without content hash."""
        mock_request.return_value = {
            "filePHID": "PHID-FILE-1",
        }

        result = self.client.allocate_file(name="test.txt", length=1024)

        mock_request.assert_called_once_with(
            "file.allocate",
            {
                "name": "test.txt",
                "contentLength": 1024,
            },
        )
        assert result["filePHID"] == "PHID-FILE-1"

    @patch("src.client.base.BasePhabricatorClient._make_request")
    def test_upload_file_success(self, mock_request):
        """Test successful file upload."""
        mock_request.return_value = {
            "filePHID": "PHID-FILE-1",
            "uri": "http://example.com/file/1",
        }

        data = b"file content"
        result = self.client.upload_file(data, name="test.txt")

        mock_request.assert_called_once_with(
            "file.upload",
            {
                "data_base64": data,
                "name": "test.txt",
            },
        )
        assert result["filePHID"] == "PHID-FILE-1"

    @patch("src.client.base.BasePhabricatorClient._make_request")
    def test_upload_file_without_name(self, mock_request):
        """Test file upload without name."""
        mock_request.return_value = {
            "filePHID": "PHID-FILE-1",
        }

        data = b"file content"
        result = self.client.upload_file(data)

        mock_request.assert_called_once_with(
            "file.upload",
            {
                "data_base64": data,
            },
        )
        assert result["filePHID"] == "PHID-FILE-1"

    @patch("src.client.base.BasePhabricatorClient._make_request")
    def test_upload_chunk_success(self, mock_request):
        """Test successful chunk upload."""
        mock_request.return_value = {
            "complete": False,
            "uploaded": 1024,
        }

        data = b"chunk content"
        result = self.client.upload_chunk(
            file_phid="PHID-FILE-1", byte_start=0, data=data
        )

        mock_request.assert_called_once_with(
            "file.uploadchunk",
            {
                "filePHID": "PHID-FILE-1",
                "byteStart": 0,
                "data": data,
            },
        )
        assert result["uploaded"] == 1024

    @patch("src.client.base.BasePhabricatorClient._make_request")
    def test_query_chunks_success(self, mock_request):
        """Test successful chunk query."""
        mock_request.return_value = {
            "complete": True,
            "chunks": [
                {"byteStart": 0, "byteEnd": 1024},
                {"byteStart": 1024, "byteEnd": 2048},
            ],
        }

        result = self.client.query_chunks("PHID-FILE-1")

        mock_request.assert_called_once_with(
            "file.querychunks",
            {
                "filePHID": "PHID-FILE-1",
            },
        )
        assert len(result["chunks"]) == 2

    @patch("src.client.base.BasePhabricatorClient._make_request")
    def test_download_file_success(self, mock_request):
        """Test successful file download."""
        mock_request.return_value = {
            "data_base64": "ZmlsZSBjb250ZW50",  # base64 encoded "file content"
            "name": "test.txt",
        }

        result = self.client.download_file("PHID-FILE-1")

        mock_request.assert_called_once_with(
            "file.download",
            {
                "phid": "PHID-FILE-1",
            },
        )
        assert result["name"] == "test.txt"

    @patch("src.client.base.BasePhabricatorClient._make_request")
    def test_get_file_info_legacy_with_id(self, mock_request):
        """Test legacy file info retrieval with ID."""
        mock_request.return_value = {
            "id": 123,
            "phid": "PHID-FILE-123",
            "name": "test.txt",
        }

        result = self.client.get_file_info_legacy(file_id=123)

        mock_request.assert_called_once_with(
            "file.info",
            {
                "id": 123,
            },
        )
        assert result["id"] == 123

    @patch("src.client.base.BasePhabricatorClient._make_request")
    def test_get_file_info_legacy_with_phid(self, mock_request):
        """Test legacy file info retrieval with PHID."""
        mock_request.return_value = {
            "id": 123,
            "phid": "PHID-FILE-123",
            "name": "test.txt",
        }

        result = self.client.get_file_info_legacy(file_phid="PHID-FILE-123")

        mock_request.assert_called_once_with(
            "file.info",
            {
                "phid": "PHID-FILE-123",
            },
        )
        assert result["phid"] == "PHID-FILE-123"

    @patch("src.client.base.BasePhabricatorClient._make_request")
    def test_get_file_info_legacy_no_parameters(self, mock_request):
        """Test legacy file info retrieval with no parameters."""
        mock_request.return_value = {
            "id": 123,
            "phid": "PHID-FILE-123",
            "name": "test.txt",
        }

        result = self.client.get_file_info_legacy()

        mock_request.assert_called_once_with("file.info", {})
        assert result["id"] == 123

    @patch("src.client.base.BasePhabricatorClient._make_request")
    def test_get_file_info_legacy_both_parameters(self, mock_request):
        """Test legacy file info retrieval with both ID and PHID."""
        mock_request.return_value = {
            "id": 123,
            "phid": "PHID-FILE-123",
            "name": "test.txt",
        }

        result = self.client.get_file_info_legacy(
            file_id=123, file_phid="PHID-FILE-123"
        )

        mock_request.assert_called_once_with(
            "file.info",
            {
                "id": 123,
                "phid": "PHID-FILE-123",
            },
        )
        assert result["id"] == 123
