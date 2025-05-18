"""
Unit tests for the MCPClient class with MCP Router.
"""

import json
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_router_use.client import MCPClient
from mcp_router_use.session import MCPSession


class TestMCPClientInitialization:
    """Tests for MCPClient initialization."""

    def test_init_empty(self):
        """Test initialization with no parameters."""
        client = MCPClient()

        assert client.config == {}
        assert client.sessions == {}
        assert client.active_sessions == []
        assert client.router_url is None

    def test_init_with_dict_config(self):
        """Test initialization with a dictionary config including router."""
        config = {
            "mcpRouter": {"router_url": "http://localhost:3282"},
            "mcpServers": {"test": {"command": "npx", "args": ["@playwright/mcp"]}}
        }
        client = MCPClient(config=config)

        assert client.config == config
        assert client.sessions == {}
        assert client.active_sessions == []
        assert client.router_url == "http://localhost:3282"

    def test_from_dict(self):
        """Test creation from a dictionary with router config."""
        config = {
            "mcpRouter": {"router_url": "http://localhost:3282"},
            "mcpServers": {"test": {"command": "npx", "args": ["@playwright/mcp"]}}
        }
        client = MCPClient.from_dict(config)

        assert client.config == config
        assert client.sessions == {}
        assert client.active_sessions == []
        assert client.router_url == "http://localhost:3282"

    def test_init_with_router_auth_token(self):
        """Test initialization with router auth token."""
        config = {
            "mcpRouter": {"router_url": "http://localhost:3282", "auth_token": "test_token"},
            "mcpServers": {"test": {"command": "npx", "args": ["@playwright/mcp"]}}
        }
        client = MCPClient(config=config)

        assert client.router_url == "http://localhost:3282"
        assert client.router_headers == {"Authorization": "Bearer test_token"}

    def test_init_with_router_headers(self):
        """Test initialization with router headers."""
        config = {
            "mcpRouter": {
                "router_url": "http://localhost:3282", 
                "headers": {"Content-Type": "application/json"}
            },
            "mcpServers": {"test": {"command": "npx", "args": ["@playwright/mcp"]}}
        }
        client = MCPClient(config=config)

        assert client.router_url == "http://localhost:3282"
        assert client.router_headers == {"Content-Type": "application/json"}

    def test_init_with_file_config(self):
        """Test initialization with a file config."""
        config = {
            "mcpRouter": {"router_url": "http://localhost:3282"},
            "mcpServers": {"test": {"command": "npx", "args": ["@playwright/mcp"]}}
        }

        # Create a temporary file with test config
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp:
            json.dump(config, temp)
            temp_path = temp.name

        try:
            # Test initialization with file path
            client = MCPClient(config=temp_path)

            assert client.config == config
            assert client.sessions == {}
            assert client.active_sessions == []
            assert client.router_url == "http://localhost:3282"
        finally:
            # Clean up temp file
            os.unlink(temp_path)

    def test_from_config_file(self):
        """Test creation from a config file."""
        config = {
            "mcpRouter": {"router_url": "http://localhost:3282"},
            "mcpServers": {"test": {"command": "npx", "args": ["@playwright/mcp"]}}
        }

        # Create a temporary file with test config
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp:
            json.dump(config, temp)
            temp_path = temp.name

        try:
            # Test creation from file path
            client = MCPClient.from_config_file(temp_path)

            assert client.config == config
            assert client.sessions == {}
            assert client.active_sessions == []
            assert client.router_url == "http://localhost:3282"
        finally:
            # Clean up temp file
            os.unlink(temp_path)


class TestMCPClientServerManagement:
    """Tests for MCPClient server management methods."""

    def test_add_server(self):
        """Test adding a server."""
        client = MCPClient()
        server_config = {"command": "npx", "args": ["@playwright/mcp"]}

        client.add_server("test", server_config)

        assert "mcpServers" in client.config
        assert client.config["mcpServers"]["test"] == server_config

    def test_add_server_to_existing(self):
        """Test adding a server to existing servers."""
        config = {"mcpServers": {"server1": {"command": "npx", "args": ["@playwright/mcp"]}}}
        client = MCPClient(config=config)
        server_config = {"command": "npx", "args": ["@websearch/mcp"]}

        client.add_server("test", server_config)

        assert "mcpServers" in client.config
        assert client.config["mcpServers"]["server1"] == {"command": "npx", "args": ["@playwright/mcp"]}
        assert client.config["mcpServers"]["test"] == server_config

    def test_remove_server(self):
        """Test removing a server."""
        config = {
            "mcpServers": {
                "server1": {"command": "npx", "args": ["@playwright/mcp"]},
                "server2": {"command": "npx", "args": ["@websearch/mcp"]},
            }
        }
        client = MCPClient(config=config)

        client.remove_server("server1")

        assert "mcpServers" in client.config
        assert "server1" not in client.config["mcpServers"]
        assert "server2" in client.config["mcpServers"]

    def test_remove_server_with_active_session(self):
        """Test removing a server with an active session."""
        config = {
            "mcpServers": {
                "server1": {"command": "npx", "args": ["@playwright/mcp"]},
                "server2": {"command": "npx", "args": ["@websearch/mcp"]},
            }
        }
        client = MCPClient(config=config)

        # Add an active session
        client.active_sessions.append("server1")

        # This should now work since we automatically remove active sessions
        client.remove_server("server1")

        assert "mcpServers" in client.config
        assert "server1" not in client.config["mcpServers"]
        assert "server1" not in client.active_sessions
        assert "server2" in client.config["mcpServers"]

    def test_get_server_names(self):
        """Test getting server names."""
        config = {
            "mcpServers": {
                "server1": {"command": "npx", "args": ["@playwright/mcp"]},
                "server2": {"command": "npx", "args": ["@websearch/mcp"]},
            }
        }
        client = MCPClient(config=config)

        server_names = client.get_server_names()

        assert len(server_names) == 2
        assert "server1" in server_names
        assert "server2" in server_names

    def test_get_server_names_empty(self):
        """Test getting server names when there are none."""
        client = MCPClient()

        server_names = client.get_server_names()

        assert len(server_names) == 0


class TestMCPClientSaveConfig:
    """Tests for MCPClient save_config method."""

    def test_save_config(self):
        """Test saving the configuration to a file."""
        config = {
            "mcpRouter": {"router_url": "http://localhost:3282"},
            "mcpServers": {"server1": {"command": "npx", "args": ["@playwright/mcp"]}}
        }
        client = MCPClient(config=config)

        # Create a temporary file path
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name

        try:
            # Test saving config
            client.save_config(temp_path)

            # Check that the file was written correctly
            with open(temp_path) as f:
                saved_config = json.load(f)

            assert saved_config == config
        finally:
            # Clean up temp file
            os.unlink(temp_path)


class TestMCPClientSessionManagement:
    """Tests for MCPClient session management methods."""

    @pytest.mark.asyncio
    @patch("mcp_router_use.client.create_connector_from_config")
    @patch("mcp_router_use.client.MCPSession")
    async def test_create_session(self, mock_session_class, mock_create_connector):
        """Test creating a session with MCP Router."""
        config = {
            "mcpRouter": {"router_url": "http://localhost:3282"},
            "mcpServers": {"server1": {"command": "npx", "args": ["@playwright/mcp"]}}
        }
        client = MCPClient(config=config)

        # Set up mocks
        mock_connector = MagicMock()
        mock_create_connector.return_value = mock_connector

        mock_session = MagicMock()
        mock_session.initialize = AsyncMock()
        mock_session_class.return_value = mock_session

        # Test create_session
        await client.create_session("server1", auto_register=False)

        # Verify behavior
        mock_create_connector.assert_called_once()
        mock_session_class.assert_called_once_with(mock_connector)
        mock_session.initialize.assert_called_once()

        # Verify state changes
        assert client.sessions["server1"] == mock_session
        assert "server1" in client.active_sessions

    @pytest.mark.asyncio
    async def test_create_session_no_servers(self):
        """Test creating a session when no servers are configured."""
        config = {"mcpRouter": {"router_url": "http://localhost:3282"}}
        client = MCPClient(config=config)

        # Test create_session raises ValueError
        with pytest.raises(ValueError) as exc_info:
            await client.create_session("server1")

        assert "No MCP servers defined in config" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_session_nonexistent_server(self):
        """Test creating a session for a non-existent server."""
        config = {
            "mcpRouter": {"router_url": "http://localhost:3282"},
            "mcpServers": {"server1": {"command": "npx", "args": ["@playwright/mcp"]}}
        }
        client = MCPClient(config=config)

        # Test create_session raises ValueError
        with pytest.raises(ValueError) as exc_info:
            await client.create_session("server2")

        assert "Server 'server2' not found in config" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("mcp_router_use.client.create_connector_from_config")
    @patch("mcp_router_use.client.MCPSession")
    async def test_create_session_no_auto_initialize(
        self, mock_session_class, mock_create_connector
    ):
        """Test creating a session without auto-initializing."""
        config = {
            "mcpRouter": {"router_url": "http://localhost:3282"},
            "mcpServers": {"server1": {"command": "npx", "args": ["@playwright/mcp"]}}
        }
        client = MCPClient(config=config)

        # Set up mocks
        mock_connector = MagicMock()
        mock_create_connector.return_value = mock_connector

        mock_session = MagicMock()
        mock_session.initialize = AsyncMock()
        mock_session_class.return_value = mock_session

        # Test create_session
        await client.create_session("server1", auto_initialize=False, auto_register=False)

        # Verify behavior
        mock_create_connector.assert_called_once()
        mock_session_class.assert_called_once_with(mock_connector)
        mock_session.initialize.assert_not_called()

        # Verify state changes
        assert client.sessions["server1"] == mock_session
        assert "server1" in client.active_sessions

    @pytest.mark.asyncio
    async def test_get_session(self):
        """Test getting an existing session."""
        client = MCPClient()

        # Add a mock session
        mock_session = MagicMock(spec=MCPSession)
        client.sessions["server1"] = mock_session

        # Test get_session
        session = await client.get_session("server1")

        assert session == mock_session

    @pytest.mark.asyncio
    async def test_get_session_nonexistent(self):
        """Test getting a non-existent session."""
        client = MCPClient()

        # Test get_session raises ValueError
        with pytest.raises(ValueError) as exc_info:
            await client.get_session("server1")

        assert "No session exists for server 'server1'" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_all_active_sessions(self):
        """Test getting all active sessions."""
        client = MCPClient()

        # Add mock sessions
        mock_session1 = MagicMock(spec=MCPSession)
        mock_session2 = MagicMock(spec=MCPSession)
        client.sessions["server1"] = mock_session1
        client.sessions["server2"] = mock_session2
        client.active_sessions = ["server1", "server2"]

        # Test get_all_active_sessions
        sessions = await client.get_all_active_sessions()

        assert len(sessions) == 2
        assert sessions["server1"] == mock_session1
        assert sessions["server2"] == mock_session2

    @pytest.mark.asyncio
    async def test_get_all_active_sessions_some_inactive(self):
        """Test getting all active sessions when some are inactive."""
        client = MCPClient()

        # Add mock sessions
        mock_session1 = MagicMock(spec=MCPSession)
        mock_session2 = MagicMock(spec=MCPSession)
        client.sessions["server1"] = mock_session1
        client.sessions["server2"] = mock_session2
        client.active_sessions = ["server1"]  # Only server1 is active

        # Test get_all_active_sessions
        sessions = await client.get_all_active_sessions()

        assert len(sessions) == 1
        assert sessions["server1"] == mock_session1
        assert "server2" not in sessions

    @pytest.mark.asyncio
    async def test_close_session(self):
        """Test closing a session."""
        client = MCPClient()

        # Add a mock session
        mock_session = MagicMock(spec=MCPSession)
        mock_session.disconnect = AsyncMock()
        client.sessions["server1"] = mock_session
        client.active_sessions = ["server1"]

        # Test close_session
        await client.close_session("server1")

        # Verify behavior
        mock_session.disconnect.assert_called_once()

        # Verify state changes
        assert "server1" not in client.sessions
        assert "server1" not in client.active_sessions

    @pytest.mark.asyncio
    async def test_close_session_nonexistent(self):
        """Test closing a non-existent session."""
        client = MCPClient()

        # Test close_session doesn't raise an exception
        await client.close_session("server1")

        # State should remain unchanged
        assert "server1" not in client.sessions
        assert "server1" not in client.active_sessions

    @pytest.mark.asyncio
    async def test_close_all_sessions(self):
        """Test closing all sessions."""
        client = MCPClient()

        # Add mock sessions
        mock_session1 = MagicMock(spec=MCPSession)
        mock_session1.disconnect = AsyncMock()
        mock_session2 = MagicMock(spec=MCPSession)
        mock_session2.disconnect = AsyncMock()

        client.sessions["server1"] = mock_session1
        client.sessions["server2"] = mock_session2
        client.active_sessions = ["server1", "server2"]

        # Test close_all_sessions
        await client.close_all_sessions()

        # Verify behavior
        mock_session1.disconnect.assert_called_once()
        mock_session2.disconnect.assert_called_once()

        # Verify state changes
        assert len(client.sessions) == 0
        assert len(client.active_sessions) == 0

    @pytest.mark.asyncio
    async def test_close_all_sessions_one_fails(self):
        """Test closing all sessions when one fails."""
        client = MCPClient()

        # Add mock sessions
        mock_session1 = MagicMock(spec=MCPSession)
        mock_session1.disconnect = AsyncMock(side_effect=Exception("Disconnect failed"))
        mock_session2 = MagicMock(spec=MCPSession)
        mock_session2.disconnect = AsyncMock()

        client.sessions["server1"] = mock_session1
        client.sessions["server2"] = mock_session2
        client.active_sessions = ["server1", "server2"]

        # Test close_all_sessions
        with pytest.raises(Exception) as exc_info:
            await client.close_all_sessions()
            
        assert "Disconnect failed" in str(exc_info.value)
        
        # Both sessions should be gone after close_all_sessions
        assert len(client.sessions) == 0
        assert len(client.active_sessions) == 0
