"""
Connectors for MCP Router.

This module provides interfaces for connecting to MCP implementations
through MCP Router.
"""

from .base import BaseConnector
from .http import HttpConnector

__all__ = [
    "BaseConnector", 
    "HttpConnector"
]
