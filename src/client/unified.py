from typing import Optional

import httpx

from .differential import DifferentialClient
from .diffusion import DiffusionClient
from .file import FileClient
from .maniphest import ManiphestClient
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
from .project import ProjectClient
from .user import UserClient


class PhabricatorClient(object):
    def __init__(
        self,
        api_url: str,
        api_token: str,
        proxy: Optional[str] = None,
        disable_cert_verify: Optional[bool] = False,
    ):
        self.api_url = api_url.rstrip("/") + "/"
        self.api_token = api_token

        self.http_client = httpx.Client(
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)",
            },
            timeout=30,
            follow_redirects=True,
            proxy=proxy,
            verify=not disable_cert_verify,
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
