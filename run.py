#!/usr/bin/env python3
"""
Main entry point for running the Conduit MCP server.
Similar to Django's manage.py - run from project root.
"""

import sys
from pathlib import Path

# Add project root to Python path (like Django does)
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now we can import directly like in Django
from src.conduit import PhabricatorConfig, mcp  # noqa: E402

if __name__ == "__main__":
    config = PhabricatorConfig()

    print("Starting Conduit MCP Server...")
    print(f"Phabricator URL: {config.url}")
    print(f"Token configured: {'Yes' if config.token else 'No'}")

    mcp.run(transport="stdio")
