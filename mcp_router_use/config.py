"""
Configuration loader for MCP session.

This module provides functionality to load MCP configuration from JSON files
and create appropriate connectors for MCP Router.
"""

import json
from typing import Any, Dict

from .connectors import BaseConnector, HttpConnector
from .logging import logger


def load_config_file(filepath: str) -> Dict[str, Any]:
    """Load a configuration file.

    Args:
        filepath: Path to the configuration file

    Returns:
        The parsed configuration
    """
    with open(filepath) as f:
        return json.load(f)


def create_connector_from_config(config: Dict[str, Any]) -> BaseConnector:
    """Create a connector based on server configuration.

    Args:
        config: The server configuration section

    Returns:
        A configured connector instance
    """
    # HTTP connector for MCP Router connection
    if "url" in config:
        headers = config.get("headers", {})
        auth_token = config.get("auth_token")
        
        # Direct HttpConnector creation with auth token passed separately
        return HttpConnector(
            base_url=config["url"],
            headers=headers,
            auth_token=auth_token,
        )
        
    raise ValueError("Cannot determine connector type from config. Expected 'url' for MCP Router connection.")
