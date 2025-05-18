"""
Unit tests for the config module.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch

from mcp_router_use.config import create_connector_from_config, load_config_file
from mcp_router_use.connectors import HttpConnector


class TestConfigLoading(unittest.TestCase):
    """Tests for configuration loading functions."""

    def test_load_config_file(self):
        """Test loading a configuration file."""
        test_config = {
            "mcpRouter": {"router_url": "http://localhost:3282"},
            "mcpServers": {"test": {"command": "npx", "args": ["@playwright/mcp"]}}
        }

        # Create a temporary file with test config
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp:
            json.dump(test_config, temp)
            temp_path = temp.name

        try:
            # Test loading from file
            loaded_config = load_config_file(temp_path)
            self.assertEqual(loaded_config, test_config)
        finally:
            # Clean up temp file
            os.unlink(temp_path)

    def test_load_config_file_nonexistent(self):
        """Test loading a non-existent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            load_config_file("/tmp/nonexistent_file.json")


class TestConnectorCreation(unittest.TestCase):
    """Tests for connector creation from configuration."""

    def test_create_http_connector(self):
        """Test creating an HTTP connector from config."""
        server_config = {
            "url": "http://localhost:3282/mcp",
            "headers": {"Content-Type": "application/json"},
            "auth_token": "test_token",
        }

        connector = create_connector_from_config(server_config)

        self.assertIsInstance(connector, HttpConnector)
        self.assertEqual(connector.base_url, "http://localhost:3282/mcp")
        self.assertEqual(
            connector.headers,
            {"Content-Type": "application/json", "Authorization": "Bearer test_token"},
        )
        self.assertEqual(connector.auth_token, "test_token")

    def test_create_http_connector_minimal(self):
        """Test creating an HTTP connector with minimal config."""
        server_config = {"url": "http://localhost:3282/mcp"}

        connector = create_connector_from_config(server_config)

        self.assertIsInstance(connector, HttpConnector)
        self.assertEqual(connector.base_url, "http://localhost:3282/mcp")
        self.assertEqual(connector.headers, {})
        self.assertIsNone(connector.auth_token)

    def test_create_connector_invalid_config(self):
        """Test creating a connector with invalid config raises ValueError."""
        server_config = {"invalid": "config"}

        with self.assertRaises(ValueError) as context:
            create_connector_from_config(server_config)

        self.assertEqual(
            str(context.exception), 
            "Cannot determine connector type from config. Expected 'url' for MCP Router connection."
        )
