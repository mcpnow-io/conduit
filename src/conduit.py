import argparse
import os

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

from src.client import PhabricatorClient
from src.main_tools import register_tools


class PhabricatorConfig(object):
    def __init__(self, token=None, require_token=True):
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


class ConduitApp:
    """Main application class for Conduit MCP Server."""

    def __init__(self, config: PhabricatorConfig, use_sse: bool = False):
        self.config = config
        self.use_sse = use_sse
        self.mcp = FastMCP("Conduit")
        self._client = None

    def get_client(self):
        """Get or create a Phabricator client instance."""
        if self._client is not None:
            return self._client

        headers = get_http_headers()
        http_token = headers.get("x-phabricator-token")

        if http_token:
            if len(http_token) != 32:
                raise ValueError(
                    "PHABRICATOR_TOKEN from HTTP header must be exactly 32 characters long"
                )

            self._client = PhabricatorClient(
                self.config.url,
                http_token,
                proxy=self.config.proxy,
                disable_cert_verify=self.config.disable_cert_verify,
            )
        elif self.use_sse:
            raise ValueError("Must provide X-PHABRICATOR-TOKEN.")
        else:
            if not self.config.token:
                raise ValueError("PHABRICATOR_TOKEN is required for stdio mode")
            self._client = PhabricatorClient(
                self.config.url,
                self.config.token,
                proxy=self.config.proxy,
                disable_cert_verify=self.config.disable_cert_verify,
            )
        return self._client

    def register_tools(self):
        """Register all MCP tools."""
        register_tools(self.mcp, self.get_client)

    def run_sse_mode(self, host: str, port: int):
        """Run the application in SSE mode."""
        print(f"Starting in HTTP/SSE mode on {host}:{port}")
        self.mcp.run(
            transport="sse",
            host=host,
            port=port,
            path="/sse",
        )

    def run_stdio_mode(self):
        """Run the application in stdio mode."""
        print("Starting in stdio mode")
        self.mcp.run(transport="stdio")


# Global app instance
_app = None


def print_server_info(config):
    """Print server configuration information."""
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
    """Check if SSE transport should be used based on command line arguments."""
    import sys

    sse_args = ["--host", "-H", "--port", "-p"]
    return any(arg in sys.argv for arg in sse_args)


def main():
    """Main entry point for the Conduit MCP Server."""
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

    # Create and run the application
    app = ConduitApp(config, use_sse)
    app.register_tools()

    if use_sse:
        app.run_sse_mode(args.host, args.port)
    else:
        app.run_stdio_mode()


# Backward compatibility functions
def get_config():
    """Get configuration for backward compatibility."""
    return PhabricatorConfig(require_token=False)


def get_client():
    """Get client for backward compatibility."""
    config = get_config()
    return PhabricatorClient(
        config.url,
        config.token or "dummy_token",
        proxy=config.proxy,
        disable_cert_verify=config.disable_cert_verify,
    )


if __name__ == "__main__":
    main()
