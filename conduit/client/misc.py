from typing import Any, Dict, List

from conduit.client.base import BasePhabricatorClient


class ConduitClient(BasePhabricatorClient):
    def ping(self) -> Dict[str, Any]:
        """
        Basic ping for monitoring or health check.

        Returns:
            Ping response
        """
        return self._make_request("conduit.ping")

    def get_capabilities(self) -> Dict[str, Any]:
        """
        List capabilities, wire formats, and authentication protocols available.

        Returns:
            Server capabilities
        """
        return self._make_request("conduit.getcapabilities")

    def query_methods(self) -> Dict[str, Any]:
        """
        Returns the parameters of the Conduit methods.

        Returns:
            Available methods
        """
        return self._make_request("conduit.query")

    def connect(self, client: str, client_version: str) -> Dict[str, Any]:
        """
        Connect a session-based client.

        Args:
            client: Client name
            client_version: Client version

        Returns:
            Connection information
        """
        return self._make_request(
            "conduit.connect", {"client": client, "clientVersion": client_version}
        )


class HarbormasterClient(BasePhabricatorClient):
    """
    Client for Harbormaster (Build System) API operations.
    """

    def search_builds(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Find out information about builds.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Build information
        """
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints

        return self._make_request("harbormaster.build.search", params)

    def search_buildables(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Find out information about buildables.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Buildable information
        """
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints

        return self._make_request("harbormaster.buildable.search", params)

    def search_build_plans(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Retrieve information about Harbormaster build plans.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Build plan information
        """
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints

        return self._make_request("harbormaster.buildplan.search", params)

    def send_message(
        self, build_target_phid: str, message_type: str, data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Modify running builds, and report build results.

        Args:
            build_target_phid: Build target PHID
            message_type: Message type
            data: Message data

        Returns:
            Result
        """
        params = {"buildTargetPHID": build_target_phid, "type": message_type}
        if data:
            params.update(data)

        return self._make_request("harbormaster.sendmessage", params)


class PasteClient(BasePhabricatorClient):
    """
    Client for Paste (Code Snippets) API operations.
    """

    def search_pastes(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Read information about pastes.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Paste information
        """
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints

        return self._make_request("paste.search", params)

    def edit_paste(
        self, transactions: List[Dict[str, Any]], object_identifier: str = None
    ) -> Dict[str, Any]:
        """
        Apply transactions to create a new paste or edit an existing one.

        Args:
            transactions: List of transaction objects
            object_identifier: Existing paste identifier to update

        Returns:
            Paste data
        """
        params = {"transactions": transactions}
        if object_identifier:
            params["objectIdentifier"] = object_identifier

        return self._make_request("paste.edit", params)

    def create_paste(
        self, title: str, content: str, language: str = None
    ) -> Dict[str, Any]:
        """
        Create a new paste.

        Args:
            title: Paste title
            content: Paste content
            language: Programming language

        Returns:
            Created paste data
        """
        transactions = [
            {"type": "title", "value": title},
            {"type": "text", "value": content},
        ]

        if language:
            transactions.append({"type": "language", "value": language})

        return self.edit_paste(transactions)


class PhrictionClient(BasePhabricatorClient):
    """
    Client for Phriction (Wiki) API operations.
    """

    def search_documents(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Read information about Phriction documents.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Document information
        """
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints

        return self._make_request("phriction.document.search", params)

    def search_content(
        self, constraints: Dict[str, Any] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Read information about Phriction document history.

        Args:
            constraints: Search constraints
            limit: Maximum number of results to return

        Returns:
            Content history information
        """
        params = {"limit": limit}
        if constraints:
            params["constraints"] = constraints

        return self._make_request("phriction.content.search", params)

    def create_document(self, path: str, title: str, content: str) -> Dict[str, Any]:
        """
        Create a Phriction document.

        Args:
            path: Document path
            title: Document title
            content: Document content

        Returns:
            Created document data
        """
        return self._make_request(
            "phriction.create", {"slug": path, "title": title, "content": content}
        )

    def edit_document(
        self, path: str, title: str = None, content: str = None
    ) -> Dict[str, Any]:
        """
        Update a Phriction document.

        Args:
            path: Document path
            title: Document title
            content: Document content

        Returns:
            Updated document data
        """
        params = {"slug": path}
        if title:
            params["title"] = title
        if content:
            params["content"] = content

        return self._make_request("phriction.edit", params)


class RemarkupClient(BasePhabricatorClient):
    """
    Client for Remarkup (Markup) processing operations.
    """

    def process_text(self, text: str, context: str = None) -> Dict[str, Any]:
        """
        Process text through remarkup.

        Args:
            text: Text to process
            context: Processing context

        Returns:
            Processed text
        """
        params = {"text": text}
        if context:
            params["context"] = context

        return self._make_request("remarkup.process", params)


class MacroClient(BasePhabricatorClient):
    """
    Client for Macro (Image Macros) API operations.
    """

    def edit_macro(
        self, transactions: List[Dict[str, Any]], object_identifier: str = None
    ) -> Dict[str, Any]:
        """
        Apply transactions to create a new macro or edit an existing one.

        Args:
            transactions: List of transaction objects
            object_identifier: Existing macro identifier to update

        Returns:
            Macro data
        """
        params = {"transactions": transactions}
        if object_identifier:
            params["objectIdentifier"] = object_identifier

        return self._make_request("macro.edit", params)

    def query_macros(self, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Retrieve image macro information.

        Args:
            constraints: Query constraints

        Returns:
            Macro information
        """
        params = constraints or {}
        return self._make_request("macro.query", params)


class FlagClient(BasePhabricatorClient):
    """
    Client for Flag API operations.
    """

    def edit_flag(
        self, object_phid: str, flag: int, note: str = None
    ) -> Dict[str, Any]:
        """
        Create or modify a flag.

        Args:
            object_phid: Object PHID to flag
            flag: Flag color/type
            note: Optional note

        Returns:
            Flag data
        """
        params = {"objectPHID": object_phid, "flag": flag}
        if note:
            params["note"] = note

        return self._make_request("flag.edit", params)

    def delete_flag(self, object_phid: str) -> Dict[str, Any]:
        """
        Clear a flag.

        Args:
            object_phid: Object PHID

        Returns:
            Result
        """
        return self._make_request("flag.delete", {"objectPHID": object_phid})

    def query_flags(
        self, object_phids: List[str] = None, owner_phids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Query flag markers.

        Args:
            object_phids: Object PHIDs to query
            owner_phids: Owner PHIDs to query

        Returns:
            Flag information
        """
        params = {}
        if object_phids:
            params["objectPHIDs"] = object_phids
        if owner_phids:
            params["ownerPHIDs"] = owner_phids

        return self._make_request("flag.query", params)


class PhidClient(BasePhabricatorClient):
    """
    Client for PHID (Object Identifier) operations.
    """

    def lookup_objects(self, names: List[str]) -> Dict[str, Any]:
        """
        Look up objects by name.

        Args:
            names: List of object names

        Returns:
            Object information
        """
        return self._make_request("phid.lookup", {"names": names})

    def query_objects(self, phids: List[str]) -> Dict[str, Any]:
        """
        Retrieve information about arbitrary PHIDs.

        Args:
            phids: List of PHIDs

        Returns:
            Object information
        """
        return self._make_request("phid.query", {"phids": phids})
