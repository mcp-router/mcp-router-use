"""
mcp_router_use - An MCP library for LLMs using MCP Router.

This library provides a unified interface for connecting different LLMs
to MCP tools through MCP Router.
"""

from importlib.metadata import version

from .agents.mcpagent import MCPAgent
from .client import MCPClient
from .config import load_config_file
from .connectors import BaseConnector, HttpConnector
from .logging import mcp_router_use_DEBUG, Logger, logger
from .session import MCPSession

__version__ = version("mcp-router-use")

__all__ = [
    "MCPAgent",
    "MCPClient",
    "MCPSession",
    "BaseConnector",
    "HttpConnector",
    "load_config_file",
    "logger",
    "mcp_router_use_DEBUG",
    "Logger",
    "set_debug",
]


# Helper function to set debug mode
def set_debug(debug=2):
    """Set the debug mode for mcp_router_use.

    Args:
        debug: Whether to enable debug mode (default: True)
    """
    Logger.set_debug(debug)
