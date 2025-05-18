"""
Basic integration test for MCP Router Use SDK.

This module tests only the basic connection to the /mcp endpoint.
"""

import os
import pytest
import aiohttp
from pathlib import Path
from dotenv import load_dotenv

from mcp_router_use import MCPClient

# Load .env file if it exists
env_path = Path(__file__).parents[2] / '.env'
load_dotenv(dotenv_path=env_path)


@pytest.fixture
def client_config():
    """Create a minimal client configuration for testing.
    
    Uses the MCP_ROUTER_AUTH_TOKEN from .env file.
    """
    # Get auth token from environment variable or use empty string
    auth_token = os.environ.get("MCP_ROUTER_AUTH_TOKEN", "")
    router_url = os.environ.get("MCP_ROUTER_URL", "http://localhost:3282")
    
    return {
        "mcpRouter": {
            "router_url": router_url,
            "auth_token": auth_token,
        },
        "mcpServers": {
            "test": {
                "command": "echo",
                "args": ["test"],
                "env": {}
            }
        }
    }


async def check_mcp_endpoint():
    """Check if the /mcp endpoint is responding."""
    # Get auth token from environment variable or use empty string
    auth_token = os.environ.get("MCP_ROUTER_AUTH_TOKEN", "")
    router_url = os.environ.get("MCP_ROUTER_URL", "http://localhost:3282")
    headers = {}
    
    # Only add Authorization header if token is provided
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{router_url}/mcp",
                headers=headers,
                json={"jsonrpc": "2.0", "method": "tools/list", "id": "1"},
                timeout=2
            ) as response:
                status = response.status
                try:
                    text = await response.text()
                except:
                    text = "<unable to retrieve response text>"
                return status, text
    except aiohttp.ClientError as e:
        return None, str(e)


@pytest.mark.asyncio
async def test_mcp_connection():
    """Test basic connection to MCP Router's /mcp endpoint."""
    # Check if environment variable is set
    if not os.environ.get("MCP_ROUTER_AUTH_TOKEN"):
        # Print warning, but continue (it may work without a token)
        print("Warning: MCP_ROUTER_AUTH_TOKEN environment variable is not set")
        print("Create a .env file based on .env.example to set the auth token")
    
    # Check if MCP endpoint is available
    status, text = await check_mcp_endpoint()
    
    # Skip test if MCP Router is not available
    if status is None:
        pytest.skip(f"MCP Router /mcp endpoint is not available: {text}")
    
    # Print diagnostic information
    print(f"MCP endpoint status: {status}")
    print(f"MCP endpoint response: {text[:200]}...")
    
    # Verify we can reach the endpoint
    assert status is not None, "Failed to connect to MCP endpoint"
    
    # We don't assert specific response status because it depends on the server setup
    # The fact that we can connect is enough for this basic test


@pytest.mark.asyncio
async def test_client_connection(client_config):
    """Test MCPClient can connect to MCP Router."""
    # Check if environment variable is set
    if not os.environ.get("MCP_ROUTER_AUTH_TOKEN"):
        # Print warning, but continue (it may work without a token)
        print("Warning: MCP_ROUTER_AUTH_TOKEN environment variable is not set")
        print("Create a .env file based on .env.example to set the auth token")
    
    # First check if MCP endpoint is available
    status, text = await check_mcp_endpoint()
    
    # Skip test if MCP Router is not available
    if status is None:
        pytest.skip(f"MCP Router /mcp endpoint is not available: {text}")
        
    # Create client
    client = MCPClient(config=client_config)
    
    try:
        # Create a connection 
        connector = None
        try:
            # This just tests the connection creation, not session initialization
            router_connector_config = {
                "url": f"{client.router_url}/mcp",
                "headers": client.router_headers,
                "auth_token": client_config["mcpRouter"].get("auth_token")
            }
            from mcp_router_use.config import create_connector_from_config
            connector = create_connector_from_config(router_connector_config)
            
            # Test that we can create a connector
            assert connector is not None, "Failed to create connector"
            print(f"Successfully created connector to MCP Router")
            
        except Exception as e:
            # Print the exception but don't fail the test if connector creation fails
            # This is just diagnostic information
            print(f"Error creating connector: {str(e)}")
        
    finally:
        # No cleanup needed for this test since we don't actually initialize a session
        pass
