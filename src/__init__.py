"""
Conduit - The MCP Server for Phabricator and Phorge

A Model Context Protocol (MCP) server that provides seamless integration
with Phabricator and Phorge APIs.
"""

__version__ = "0.1.0"
__author__ = "mcpnow.io"
__email__ = "support@mcpnow.io"

from .conduit import PhabricatorConfig, main

__all__ = ["PhabricatorConfig", "main"]
