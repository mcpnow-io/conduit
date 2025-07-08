import argparse
import os

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

from src.client import PhabricatorClient
from src.tools import register_tools


class PhabricatorConfig(object):
    def __init__(self, token=None, require_token=True):
        self.user_agent_filter = os.getenv("CONDUIT_USER_AGENT_FILTER")
        self.token = token or os.getenv("PHABRICATOR_TOKEN")
        self.url = os.getenv("PHABRICATOR_URL")
        self.proxy = os.getenv("PHABRICATOR_PROXY")
        self.disable_cert_verify = os.getenv(
            "PHABRICATOR_DISABLE_CERT_VERIFY", ""
        ).lower() in ("1", "true", "yes")

        if require_token and not self.token:
            raise ValueError("PHABRICATOR_TOKEN is required")

        if not self.url:
            raise ValueError("PHABRICATOR_URL environment variable is required")

        if self.token and len(self.token) != 32:
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
use_sse = None


def get_config():
    global config
    if config is None:
        config = PhabricatorConfig(require_token=False)
    return config


def get_client():
    global client

    headers = get_http_headers()
    http_token = headers.get("x-phabricator-token")

    config = get_config()

    if config.user_agent_filter and use_sse:
        user_agent = headers.get("user-agent", "")
        if config.user_agent_filter not in user_agent:
            raise ValueError("Access denied")

    if http_token:
        if len(http_token) != 32:
            raise ValueError(
                "PHABRICATOR_TOKEN from HTTP header must be exactly 32 characters long"
            )

        return PhabricatorClient(
            config.url,
            http_token,
            proxy=config.proxy,
            disable_cert_verify=config.disable_cert_verify,
        )
    elif use_sse:
        raise ValueError("Must provide X-PHABRICATOR-TOKEN.")
    elif not use_sse:
        if client is None:
            if not config.token:
                raise ValueError("PHABRICATOR_TOKEN is required for stdio mode")
            client = PhabricatorClient(
                config.url,
                config.token,
                proxy=config.proxy,
                disable_cert_verify=config.disable_cert_verify,
            )
        return client


def print_server_info(config):
    print("Starting Conduit MCP Server...")
    print(f"Phabricator URL: {config.url}")
    print(f"Token configured: {'Yes' if config.token else 'No'}")
    print(f"Proxy configured: {'Yes' if config.proxy else 'No'}")
    if config.proxy:
        print(f"Proxy URL: {config.proxy}")
    print(
        f"SSL certificate verification: {'Disabled' if config.disable_cert_verify else 'Enabled'}"
    )


def should_use_sse_transport() -> bool:
    import sys

    sse_args = ["--host", "-H", "--port", "-p"]
    return any(arg in sys.argv for arg in sse_args)


def run_sse_mode(args):
    print(f"Starting in HTTP/SSE mode on {args.host}:{args.port}")
    mcp.run(
        transport="sse",
        host=args.host,
        port=args.port,
        path="/sse",
    )


def run_stdio_mode():
    print("Starting in stdio mode")
    mcp.run(transport="stdio")


def main():
    global config, use_sse

    parser = argparse.ArgumentParser(
        description="Conduit MCP Server for Phabricator and Phorge"
    )
    parser.add_argument(
        "--host",
        "-H",
        default="127.0.0.1",
        help="Host to bind to for SSE transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Port to bind to for SSE transport (default: 8000)",
    )

    args = parser.parse_args()

    use_sse = should_use_sse_transport()

    if use_sse:
        config = PhabricatorConfig(require_token=False)
        print_server_info(config)

        print(
            "Note: In HTTP/SSE mode, PHABRICATOR_TOKEN should be provided via HTTP headers:"
        )
        print("  - X-PHABRICATOR-TOKEN: <token>")
    else:
        config = PhabricatorConfig(require_token=True)
        print_server_info(config)

    register_tools(mcp, get_client)

    if use_sse:
        run_sse_mode(args)
    else:
        run_stdio_mode()


if __name__ == "__main__":
    main()
