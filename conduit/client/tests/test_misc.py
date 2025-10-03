"""Tests for miscellaneous clients."""

from unittest.mock import patch

from conduit.client.misc import (
    ConduitClient,
    HarbormasterClient,
    PasteClient,
    PhrictionClient,
    RemarkupClient,
    MacroClient,
    FlagClient,
    PhidClient,
)


class TestConduitClient:
    """Test ConduitClient methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = ConduitClient(
            api_url="http://test.example.com/api/", api_token="test_token"
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_ping(self, mock_request):
        """Test conduit ping."""
        mock_request.return_value = {"status": "ok"}

        result = self.client.ping()

        mock_request.assert_called_once_with("conduit.ping")
        assert result["status"] == "ok"

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_get_capabilities(self, mock_request):
        """Test getting capabilities."""
        mock_request.return_value = {
            "authentication": ["token", "session"],
            "signatures": ["consign"],
        }

        result = self.client.get_capabilities()

        mock_request.assert_called_once_with("conduit.getcapabilities")
        assert "authentication" in result

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_query_methods(self, mock_request):
        """Test querying methods."""
        mock_request.return_value = {
            "result": {
                "user.whoami": {"description": "Get current user"},
            }
        }

        result = self.client.query_methods()

        mock_request.assert_called_once_with("conduit.query")
        assert "result" in result

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_connect(self, mock_request):
        """Test connecting client."""
        mock_request.return_value = {
            "sessionKey": "session123",
            "connectionID": 456,
        }

        result = self.client.connect("test_client", "1.0.0")

        mock_request.assert_called_once_with(
            "conduit.connect", {"client": "test_client", "clientVersion": "1.0.0"}
        )
        assert result["sessionKey"] == "session123"


class TestHarbormasterClient:
    """Test HarbormasterClient methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = HarbormasterClient(
            api_url="http://test.example.com/api/", api_token="test_token"
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_search_builds(self, mock_request):
        """Test searching builds."""
        mock_request.return_value = {
            "data": [
                {"phid": "PHID-HMBB-build1", "status": "passed"},
                {"phid": "PHID-HMBB-build2", "status": "failed"},
            ]
        }

        self.client.search_builds(constraints={"status": "passed"}, limit=10)

        mock_request.assert_called_once_with(
            "harbormaster.build.search",
            {
                "constraints": {"status": "passed"},
                "limit": 10,
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_search_builds_no_constraints(self, mock_request):
        """Test searching builds without constraints."""
        mock_request.return_value = {"data": []}

        self.client.search_builds()

        mock_request.assert_called_once_with(
            "harbormaster.build.search",
            {
                "limit": 100,
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_search_buildables(self, mock_request):
        """Test searching buildables."""
        mock_request.return_value = {
            "data": [
                {"phid": "PHID-HMBL-buildable1", "container": "PHID-REPO-1"},
            ]
        }

        self.client.search_buildables(limit=5)

        mock_request.assert_called_once_with(
            "harbormaster.buildable.search",
            {
                "limit": 5,
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_search_build_plans(self, mock_request):
        """Test searching build plans."""
        mock_request.return_value = {
            "data": [
                {"phid": "PHID-HMCP-plan1", "name": "CI Build"},
            ]
        }

        self.client.search_build_plans(constraints={"name": "CI"}, limit=10)

        mock_request.assert_called_once_with(
            "harbormaster.buildplan.search",
            {
                "constraints": {"name": "CI"},
                "limit": 10,
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_send_message(self, mock_request):
        """Test sending message to build."""
        mock_request.return_value = {"saved": True}

        self.client.send_message(
            build_target_phid="PHID-HMBT-target1",
            message_type="pass",
            data={"message": "Build completed successfully"},
        )

        mock_request.assert_called_once_with(
            "harbormaster.sendmessage",
            {
                "buildTargetPHID": "PHID-HMBT-target1",
                "type": "pass",
                "message": "Build completed successfully",
            },
        )


class TestPasteClient:
    """Test PasteClient methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = PasteClient(
            api_url="http://test.example.com/api/", api_token="test_token"
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_search_pastes(self, mock_request):
        """Test searching pastes."""
        mock_request.return_value = {
            "data": [
                {"phid": "PHID-PAST-paste1", "title": "Test Paste"},
            ]
        }

        self.client.search_pastes(
            constraints={"authorPHIDs": ["PHID-USER-1"]}, limit=10
        )

        mock_request.assert_called_once_with(
            "paste.search",
            {
                "constraints": {"authorPHIDs": ["PHID-USER-1"]},
                "limit": 10,
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_edit_paste_create(self, mock_request):
        """Test creating a new paste."""
        mock_request.return_value = {
            "object": {"phid": "PHID-PAST-new", "title": "New Paste"},
        }

        transactions = [
            {"type": "title", "value": "New Paste"},
            {"type": "text", "value": "Paste content"},
        ]

        self.client.edit_paste(transactions)

        mock_request.assert_called_once_with(
            "paste.edit",
            {
                "transactions": transactions,
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_edit_paste_update(self, mock_request):
        """Test updating an existing paste."""
        mock_request.return_value = {
            "object": {"phid": "PHID-PAST-updated", "title": "Updated Paste"},
        }

        transactions = [{"type": "title", "value": "Updated Paste"}]

        self.client.edit_paste(transactions, object_identifier="PHID-PAST-existing")

        mock_request.assert_called_once_with(
            "paste.edit",
            {
                "transactions": transactions,
                "objectIdentifier": "PHID-PAST-existing",
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_create_paste(self, mock_request):
        """Test creating a new paste with convenience method."""
        mock_request.return_value = {
            "object": {"phid": "PHID-PAST-new", "title": "Test Paste"},
        }

        self.client.create_paste(
            title="Test Paste", content="print('hello world')", language="python"
        )

        expected_transactions = [
            {"type": "title", "value": "Test Paste"},
            {"type": "text", "value": "print('hello world')"},
            {"type": "language", "value": "python"},
        ]

        mock_request.assert_called_once_with(
            "paste.edit",
            {
                "transactions": expected_transactions,
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_create_paste_without_language(self, mock_request):
        """Test creating a paste without specifying language."""
        mock_request.return_value = {
            "object": {"phid": "PHID-PAST-new", "title": "Simple Paste"},
        }

        self.client.create_paste(title="Simple Paste", content="Simple content")

        expected_transactions = [
            {"type": "title", "value": "Simple Paste"},
            {"type": "text", "value": "Simple content"},
        ]

        mock_request.assert_called_once_with(
            "paste.edit",
            {
                "transactions": expected_transactions,
            },
        )


class TestPhrictionClient:
    """Test PhrictionClient methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = PhrictionClient(
            api_url="http://test.example.com/api/", api_token="test_token"
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_search_documents(self, mock_request):
        """Test searching documents."""
        mock_request.return_value = {
            "data": [
                {"phid": "PHID-WIKI-doc1", "title": "Home Page"},
            ]
        }

        self.client.search_documents(limit=10)

        mock_request.assert_called_once_with(
            "phriction.document.search",
            {
                "limit": 10,
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_search_content(self, mock_request):
        """Test searching content history."""
        mock_request.return_value = {
            "data": [
                {"phid": "PHID-WIKI-content1", "version": 2},
            ]
        }

        self.client.search_content(constraints={"documentPHID": "PHID-WIKI-doc1"})

        mock_request.assert_called_once_with(
            "phriction.content.search",
            {
                "constraints": {"documentPHID": "PHID-WIKI-doc1"},
                "limit": 100,
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_create_document(self, mock_request):
        """Test creating a document."""
        mock_request.return_value = {
            "document": {"phid": "PHID-WIKI-new", "title": "New Page"},
        }

        self.client.create_document(
            path="projects/new_page",
            title="New Page",
            content="# New Page\n\nContent here.",
        )

        mock_request.assert_called_once_with(
            "phriction.create",
            {
                "slug": "projects/new_page",
                "title": "New Page",
                "content": "# New Page\n\nContent here.",
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_edit_document(self, mock_request):
        """Test editing a document."""
        mock_request.return_value = {
            "document": {"phid": "PHID-WIKI-updated", "title": "Updated Page"},
        }

        self.client.edit_document(
            path="projects/existing_page",
            title="Updated Page",
            content="Updated content",
        )

        mock_request.assert_called_once_with(
            "phriction.edit",
            {
                "slug": "projects/existing_page",
                "title": "Updated Page",
                "content": "Updated content",
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_edit_document_partial(self, mock_request):
        """Test editing only title of a document."""
        mock_request.return_value = {
            "document": {"phid": "PHID-WIKI-updated", "title": "New Title"},
        }

        self.client.edit_document(path="projects/existing_page", title="New Title")

        mock_request.assert_called_once_with(
            "phriction.edit",
            {
                "slug": "projects/existing_page",
                "title": "New Title",
            },
        )


class TestRemarkupClient:
    """Test RemarkupClient methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = RemarkupClient(
            api_url="http://test.example.com/api/", api_token="test_token"
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_process_text(self, mock_request):
        """Test processing remarkup text."""
        mock_request.return_value = {
            "output": "<p>Processed <strong>text</strong></p>",
        }

        self.client.process_text("**Bold** text")

        mock_request.assert_called_once_with(
            "remarkup.process",
            {
                "text": "**Bold** text",
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_process_text_with_context(self, mock_request):
        """Test processing remarkup text with context."""
        mock_request.return_value = {
            "output": "<p>Text with context</p>",
        }

        self.client.process_text("Text with context", context="PHID-WIKI-doc1")

        mock_request.assert_called_once_with(
            "remarkup.process",
            {
                "text": "Text with context",
                "context": "PHID-WIKI-doc1",
            },
        )


class TestMacroClient:
    """Test MacroClient methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = MacroClient(
            api_url="http://test.example.com/api/", api_token="test_token"
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_edit_macro_create(self, mock_request):
        """Test creating a new macro."""
        mock_request.return_value = {
            "object": {"phid": "PHID-MACRO-new", "name": "test_macro"},
        }

        transactions = [
            {"type": "name", "value": "test_macro"},
            {"type": "filePHID", "value": "PHID-FILE-1"},
        ]

        self.client.edit_macro(transactions)

        mock_request.assert_called_once_with(
            "macro.edit",
            {
                "transactions": transactions,
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_edit_macro_update(self, mock_request):
        """Test updating an existing macro."""
        mock_request.return_value = {
            "object": {"phid": "PHID-MACRO-updated", "name": "updated_macro"},
        }

        transactions = [{"type": "name", "value": "updated_macro"}]

        self.client.edit_macro(transactions, object_identifier="PHID-MACRO-existing")

        mock_request.assert_called_once_with(
            "macro.edit",
            {
                "transactions": transactions,
                "objectIdentifier": "PHID-MACRO-existing",
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_query_macros(self, mock_request):
        """Test querying macros."""
        mock_request.return_value = {
            "data": [
                {"phid": "PHID-MACRO-1", "name": "smile"},
                {"phid": "PHID-MACRO-2", "name": "thumbs_up"},
            ],
        }

        constraints = {"name": "smile"}
        self.client.query_macros(constraints)

        mock_request.assert_called_once_with("macro.query", constraints)

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_query_macros_no_constraints(self, mock_request):
        """Test querying macros without constraints."""
        mock_request.return_value = {"data": []}

        self.client.query_macros()

        mock_request.assert_called_once_with("macro.query", {})


class TestFlagClient:
    """Test FlagClient methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = FlagClient(
            api_url="http://test.example.com/api/", api_token="test_token"
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_edit_flag(self, mock_request):
        """Test creating/editing a flag."""
        mock_request.return_value = {
            "object": {"phid": "PHID-FLAG-1", "color": "red"},
        }

        self.client.edit_flag(
            object_phid="PHID-TASK-1",
            flag=8,  # Red flag
            note="Important task",
        )

        mock_request.assert_called_once_with(
            "flag.edit",
            {
                "objectPHID": "PHID-TASK-1",
                "flag": 8,
                "note": "Important task",
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_edit_flag_without_note(self, mock_request):
        """Test creating a flag without note."""
        mock_request.return_value = {
            "object": {"phid": "PHID-FLAG-2", "color": "green"},
        }

        self.client.edit_flag(
            object_phid="PHID-TASK-2",
            flag=3,  # Green flag
        )

        mock_request.assert_called_once_with(
            "flag.edit",
            {
                "objectPHID": "PHID-TASK-2",
                "flag": 3,
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_delete_flag(self, mock_request):
        """Test deleting a flag."""
        mock_request.return_value = {"deleted": True}

        self.client.delete_flag("PHID-TASK-1")

        mock_request.assert_called_once_with(
            "flag.delete",
            {
                "objectPHID": "PHID-TASK-1",
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_query_flags_by_objects(self, mock_request):
        """Test querying flags by object PHIDs."""
        mock_request.return_value = {
            "data": [
                {"objectPHID": "PHID-TASK-1", "color": "red"},
                {"objectPHID": "PHID-TASK-2", "color": "green"},
            ],
        }

        self.client.query_flags(object_phids=["PHID-TASK-1", "PHID-TASK-2"])

        mock_request.assert_called_once_with(
            "flag.query",
            {
                "objectPHIDs": ["PHID-TASK-1", "PHID-TASK-2"],
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_query_flags_by_owners(self, mock_request):
        """Test querying flags by owner PHIDs."""
        mock_request.return_value = {
            "data": [
                {"objectPHID": "PHID-TASK-1", "ownerPHID": "PHID-USER-1"},
            ],
        }

        self.client.query_flags(owner_phids=["PHID-USER-1", "PHID-USER-2"])

        mock_request.assert_called_once_with(
            "flag.query",
            {
                "ownerPHIDs": ["PHID-USER-1", "PHID-USER-2"],
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_query_flags_both_parameters(self, mock_request):
        """Test querying flags with both object and owner PHIDs."""
        mock_request.return_value = {"data": []}

        self.client.query_flags(
            object_phids=["PHID-TASK-1"], owner_phids=["PHID-USER-1"]
        )

        mock_request.assert_called_once_with(
            "flag.query",
            {
                "objectPHIDs": ["PHID-TASK-1"],
                "ownerPHIDs": ["PHID-USER-1"],
            },
        )


class TestPhidClient:
    """Test PhidClient methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = PhidClient(
            api_url="http://test.example.com/api/", api_token="test_token"
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_lookup_objects(self, mock_request):
        """Test looking up objects by name."""
        mock_request.return_value = {
            "result": [
                {"name": "T123", "phid": "PHID-TASK-123"},
                {"name": "D456", "phid": "PHID-DREV-456"},
            ],
        }

        self.client.lookup_objects(["T123", "D456"])

        mock_request.assert_called_once_with(
            "phid.lookup",
            {
                "names": ["T123", "D456"],
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_query_objects(self, mock_request):
        """Test querying objects by PHIDs."""
        mock_request.return_value = {
            "result": [
                {"phid": "PHID-TASK-123", "type": "TASK", "name": "Task Title"},
                {"phid": "PHID-USER-456", "type": "USER", "name": "username"},
            ],
        }

        self.client.query_objects(["PHID-TASK-123", "PHID-USER-456"])

        mock_request.assert_called_once_with(
            "phid.query",
            {
                "phids": ["PHID-TASK-123", "PHID-USER-456"],
            },
        )

    @patch("conduit.client.base.BasePhabricatorClient._make_request")
    def test_query_objects_empty_list(self, mock_request):
        """Test querying objects with empty PHID list."""
        mock_request.return_value = {"result": []}

        self.client.query_objects([])

        mock_request.assert_called_once_with(
            "phid.query",
            {
                "phids": [],
            },
        )
