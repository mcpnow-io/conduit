import httpx

from .differential import AsyncDifferentialClient, DifferentialClient
from .diffusion import AsyncDiffusionClient, DiffusionClient
from .file import AsyncFileClient, FileClient
from .maniphest import AsyncManiphestClient, ManiphestClient
from .misc import (
    ConduitClient,
    FlagClient,
    HarbormasterClient,
    MacroClient,
    PasteClient,
    PhidClient,
    PhrictionClient,
    RemarkupClient,
)
from .project import AsyncProjectClient, ProjectClient
from .user import AsyncUserClient, UserClient


class PhabricatorClient(object):
    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url.rstrip("/") + "/"
        self.api_token = api_token

        self.http_client = httpx.Client(
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)",
            },
            timeout=30,
            follow_redirects=True,
        )

        self.maniphest = ManiphestClient(api_url, api_token, self.http_client)
        self.differential = DifferentialClient(api_url, api_token, self.http_client)
        self.diffusion = DiffusionClient(api_url, api_token, self.http_client)
        self.project = ProjectClient(api_url, api_token, self.http_client)
        self.user = UserClient(api_url, api_token, self.http_client)
        self.file = FileClient(api_url, api_token, self.http_client)
        self.conduit = ConduitClient(api_url, api_token, self.http_client)
        self.harbormaster = HarbormasterClient(api_url, api_token, self.http_client)
        self.paste = PasteClient(api_url, api_token, self.http_client)
        self.phriction = PhrictionClient(api_url, api_token, self.http_client)
        self.remarkup = RemarkupClient(api_url, api_token, self.http_client)
        self.macro = MacroClient(api_url, api_token, self.http_client)
        self.flag = FlagClient(api_url, api_token, self.http_client)
        self.phid = PhidClient(api_url, api_token, self.http_client)

    def close(self):
        if self.http_client:
            self.http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncPhabricatorClient:
    """
    Unified async Phabricator client that provides access to all API modules.

    This client creates async sub-clients for each major Phabricator component
    and shares a single HTTP connection between them for efficiency.
    """

    def __init__(self, api_url: str, api_token: str):
        """
        Initialize the unified async Phabricator client.

        Args:
            api_url: Base URL for the Phabricator API
            api_token: API token for authentication
        """
        self.api_url = api_url.rstrip("/") + "/"
        self.api_token = api_token

        # Create shared async HTTP client
        self.http_client = httpx.AsyncClient(
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)",
            },
            timeout=30.0,
            follow_redirects=True,
        )

        # Initialize all async sub-clients
        self.maniphest = AsyncManiphestClient(api_url, api_token, self.http_client)
        self.differential = AsyncDifferentialClient(
            api_url, api_token, self.http_client
        )
        self.diffusion = AsyncDiffusionClient(api_url, api_token, self.http_client)
        self.project = AsyncProjectClient(api_url, api_token, self.http_client)
        self.user = AsyncUserClient(api_url, api_token, self.http_client)
        self.file = AsyncFileClient(api_url, api_token, self.http_client)

    # Convenience methods for backward compatibility
    async def test_connection(self):
        """Test the API connection asynchronously."""
        return await self.user.test_connection()

    async def search_tasks(self, constraints=None, limit=100):
        """Search for tasks asynchronously."""
        return await self.maniphest.search_tasks(constraints, limit)

    async def create_task(
        self, title, description="", owner_phid=None, project_phids=None, priority=None
    ):
        """Create a task asynchronously."""
        return await self.maniphest.create_task(
            title, description, owner_phid, project_phids, priority
        )

    async def close(self):
        """Close the async HTTP client."""
        if self.http_client:
            await self.http_client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
