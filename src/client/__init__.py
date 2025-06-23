from .base import PhabricatorAPIError
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
from .unified import AsyncPhabricatorClient, PhabricatorClient
from .user import AsyncUserClient, UserClient

__all__ = [
    # Main clients (backward compatible)
    "PhabricatorClient",
    "AsyncPhabricatorClient",
    "PhabricatorAPIError",
    # Module-specific clients
    "ManiphestClient",
    "AsyncManiphestClient",
    "DifferentialClient",
    "AsyncDifferentialClient",
    "DiffusionClient",
    "AsyncDiffusionClient",
    "ProjectClient",
    "AsyncProjectClient",
    "UserClient",
    "AsyncUserClient",
    "FileClient",
    "AsyncFileClient",
    # Specialized clients
    "ConduitClient",
    "HarbormasterClient",
    "PasteClient",
    "PhrictionClient",
    "RemarkupClient",
    "MacroClient",
    "FlagClient",
    "PhidClient",
]
