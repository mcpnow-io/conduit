import os

from fastmcp import FastMCP

from src.client import PhabricatorClient
from src.tools import register_tools


class PhabricatorConfig(object):
    def __init__(self):
        self.token = os.getenv("PHABRICATOR_TOKEN")
        self.url = os.getenv("PHABRICATOR_URL")

        if not self.token:
            raise ValueError("PHABRICATOR_TOKEN environment variable is required")

        if not self.url:
            raise ValueError("PHABRICATOR_URL environment variable is required")

        if len(self.token) != 32:
            raise ValueError("PHABRICATOR_TOKEN must be exactly 32 characters long")

        if not self.url.startswith(("http://", "https://")):
            raise ValueError("PHABRICATOR_URL must start with http:// or https://")

        if self.url and not self.url.endswith("/"):
            self.url += "/"

    @property
    def api_headers(self):
        return {"Content-Type": "application/x-www-form-urlencoded"}

    @property
    def base_params(self):
        return {"api.token": self.token}


mcp = FastMCP("Conduit")

config = None
client = None


def get_config():
    global config
    if config is None:
        config = PhabricatorConfig()
    return config


def get_client():
    global client
    if client is None:
        config = get_config()
        client = PhabricatorClient(config.url, config.token)
    return client


def main():
    config = PhabricatorConfig()

    print("Starting Conduit MCP Server...")
    print(f"Phabricator URL: {config.url}")
    print(f"Token configured: {'Yes' if config.token else 'No'}")

    register_tools(mcp, get_client)

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
