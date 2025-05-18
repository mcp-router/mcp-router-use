"""
Unit tests for the MCPClient Router-specific functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_router_use.client import MCPClient


@pytest.fixture
def router_client():
    """Create a client with MCP Router configuration."""
    config = {
        "mcpRouter": {
            "router_url": "http://localhost:3282",
            "auth_token": "test_token"
        },
        "mcpServers": {
            "test-server": {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-test"]
            }
        }
    }
    return MCPClient(config=config)


class TestMCPClientRouterFunctions:
    """Tests for MCPClient router-specific functions."""

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_register_server_with_router(self, mock_post, router_client):
        """Test registering a server with the router."""
        # Set up mock response for server registration
        mock_response = MagicMock()
        mock_response.status = 201
        mock_response.json = AsyncMock(
            return_value={
                "results": [
                    {
                        "name": "test-server",
                        "success": True,
                        "message": "Server added successfully"
                    }
                ]
            }
        )
        mock_post.return_value.__aenter__.return_value = mock_response

        # Call the register_server_with_router method
        server_id = await router_client.register_server_with_router("test-server")

        # Verify the POST request
        mock_post.assert_called_once()
        url = mock_post.call_args[0][0]
        headers = mock_post.call_args[1]["headers"]
        json_data = mock_post.call_args[1]["json"]

        assert url == "http://localhost:3282/api/servers"
        assert headers == {"Authorization": "Bearer test_token"}
        assert "test-server" in json_data
        assert json_data["test-server"]["command"] == "npx"
        assert json_data["test-server"]["args"] == ["@modelcontextprotocol/server-test"]

        # Verify the result and side effects
        assert server_id == "test-server"
        assert router_client.config["mcpServers"]["test-server"]["server_id"] == "test-server"

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    @patch("mcp_router_use.client.logger.warning")
    async def test_register_server_failure(self, mock_logger, mock_post, router_client):
        """Test registration failure."""
        # Set up mock response for server registration failure
        mock_response = MagicMock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value="Bad request")
        mock_post.return_value.__aenter__.return_value = mock_response

        # Call the register_server_with_router method
        server_id = await router_client.register_server_with_router("test-server")

        # Verify the POST request was made
        mock_post.assert_called_once()

        # Verify the result
        assert server_id is None
        assert "server_id" not in router_client.config["mcpServers"]["test-server"]

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_start_server_in_router(self, mock_post, router_client):
        """Test starting a server in the router."""
        # Add a server_id to the test-server configuration
        router_client.config["mcpServers"]["test-server"]["server_id"] = "test-server"

        # Set up mock response for server start
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "success": True,
                "message": "Server started successfully",
                "status": "online"
            }
        )
        mock_post.return_value.__aenter__.return_value = mock_response

        # Call the start_server_in_router method
        success = await router_client.start_server_in_router("test-server")

        # Verify the POST request
        mock_post.assert_called_once()
        url = mock_post.call_args[0][0]
        headers = mock_post.call_args[1]["headers"]

        assert url == "http://localhost:3282/api/servers/test-server/start"
        assert headers == {"Authorization": "Bearer test_token"}

        # Verify the result
        assert success is True

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    @patch("mcp_router_use.client.logger.warning")
    async def test_start_server_failure(self, mock_logger, mock_post, router_client):
        """Test server start failure."""
        # Add a server_id to the test-server configuration
        router_client.config["mcpServers"]["test-server"]["server_id"] = "test-server"

        # Set up mock response for server start failure
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal server error")
        mock_post.return_value.__aenter__.return_value = mock_response

        # Call the start_server_in_router method
        success = await router_client.start_server_in_router("test-server")

        # Verify the POST request was made
        mock_post.assert_called_once()

        # Verify the result
        assert success is False

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_get_router_servers(self, mock_get, router_client):
        """Test getting server list from the router."""
        # Set up mock response for server list
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value=[
                {
                    "id": "test-server",
                    "name": "test-server",
                    "status": "online",
                    "capabilities": ["browser"]
                },
                {
                    "id": "other-server",
                    "name": "other-server",
                    "status": "offline",
                    "capabilities": ["websearch"]
                }
            ]
        )
        mock_get.return_value.__aenter__.return_value = mock_response

        # Call the get_router_servers method
        servers = await router_client.get_router_servers()

        # Verify the GET request
        mock_get.assert_called_once()
        url = mock_get.call_args[0][0]
        headers = mock_get.call_args[1]["headers"]

        assert url == "http://localhost:3282/api/servers"
        assert headers == {"Authorization": "Bearer test_token"}

        # Verify the result
        assert len(servers) == 2
        assert servers[0]["id"] == "test-server"
        assert servers[0]["status"] == "online"
        assert servers[1]["id"] == "other-server"
        assert servers[1]["status"] == "offline"

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    @patch("mcp_router_use.client.logger.warning")
    async def test_get_router_servers_failure(self, mock_logger, mock_get, router_client):
        """Test server list retrieval failure."""
        # Set up mock response for server list failure
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal server error")
        mock_get.return_value.__aenter__.return_value = mock_response

        # Call the get_router_servers method
        servers = await router_client.get_router_servers()

        # Verify the GET request was made
        mock_get.assert_called_once()

        # Verify the result
        assert servers == []

    @pytest.mark.asyncio
    @patch("mcp_router_use.client.MCPClient.register_server_with_router")
    @patch("mcp_router_use.client.MCPClient.start_server_in_router")
    @patch("mcp_router_use.client.create_connector_from_config")
    @patch("mcp_router_use.client.MCPSession")
    async def test_create_session_with_auto_register(
        self, mock_session_class, mock_create_connector, 
        mock_start_server, mock_register_server, router_client
    ):
        """Test creating a session with auto-registration."""
        # Set up mocks
        mock_register_server.return_value = "test-server"
        mock_start_server.return_value = True
        
        mock_connector = MagicMock()
        mock_create_connector.return_value = mock_connector
        
        mock_session = MagicMock()
        mock_session.initialize = AsyncMock()
        mock_session_class.return_value = mock_session

        # Call create_session with auto_register=True
        session = await router_client.create_session("test-server", auto_register=True)

        # Verify registration and start were called
        mock_register_server.assert_called_once_with("test-server")
        mock_start_server.assert_called_once_with("test-server")
        
        # Verify connector creation
        mock_create_connector.assert_called_once()
        connector_config = mock_create_connector.call_args[0][0]
        assert connector_config["url"] == "http://localhost:3282/mcp"
        
        # Verify session creation and initialization
        mock_session_class.assert_called_once_with(mock_connector)
        mock_session.initialize.assert_called_once()
        
        # Verify the session was stored
        assert router_client.sessions["test-server"] == mock_session
        assert "test-server" in router_client.active_sessions

    @pytest.mark.asyncio
    async def test_create_session_no_router_url(self):
        """Test creating a session without router URL."""
        # Create client with no router URL
        client = MCPClient(config={
            "mcpServers": {
                "test-server": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-test"]
                }
            }
        })
        
        # Attempt to create a session
        with pytest.raises(ValueError) as excinfo:
            await client.create_session("test-server")
        
        # Verify the error message
        assert "No MCP Router URL configured" in str(excinfo.value)
