"""
Advanced example of MCP Client with auto-registration through MCP Router.

This example demonstrates how to use the MCPClient with automatic server
registration and starting through MCP Router. It also shows how to check 
if a server exists before registering it.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional

from mcp_router_use import MCPClient, set_debug

# Set debug level (0: no debug, 1: info, 2: debug)
set_debug(2)

# Configuration for multiple MCP servers
CONFIG = {
    "mcpRouter": {
        "router_url": "http://localhost:3282",
        # Uncomment and add token if required
        # "auth_token": "your_token_here",
    },
    "mcpServers": {
        "puppeteer": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
            "env": {
                "PUPPETEER_LAUNCH_OPTIONS": "{ \"headless\": false }",
                "ALLOW_DANGEROUS": "true"
            }
        },
        "web-search": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-web-search"],
            "env": {
                "API_KEY": "your_api_key_here",  # Replace with your actual API key
            }
        }
    }
}


async def find_server_by_name(client: MCPClient, name: str) -> Optional[Dict[str, Any]]:
    """Find a server by name in the MCP Router.
    
    Args:
        client: The MCPClient with Router configuration.
        name: The name to search for.
        
    Returns:
        Server information if found, None otherwise.
    """
    try:
        # Get all servers from the router
        servers = await client.get_router_servers()
        for server in servers:
            # Look for a matching name in the server info
            if server.get("name") == name:
                return server
        return None
    except Exception as e:
        print(f"Error finding server: {e}")
        return None


async def ensure_server_running(
    client: MCPClient, 
    server_name: str
) -> Optional[str]:
    """Ensure a server is registered and running.
    
    Args:
        client: The MCPClient with Router configuration.
        server_name: The name of the server in the configuration.
        
    Returns:
        The server ID if successful, None otherwise.
    """
    # First, check if the server exists in the router
    servers = await client.get_router_servers()
    server_exists = False
    server_id = None
    
    # Try to find the server by name that matches the server_name
    for server in servers:
        if server.get("name") == server_name:
            server_exists = True
            server_id = server.get("id")
            print(f"Server '{server_name}' already exists with ID: {server_id}")
            
            # Check if the server is online
            if server.get("status") != "online":
                print(f"Server '{server_name}' exists but is not online, starting...")
                started = await client.start_server_in_router(server_name)
                if not started:
                    print(f"Failed to start existing server '{server_name}'")
                    return None
                print(f"Server '{server_name}' started successfully")
            break
    
    # If the server doesn't exist, register and start it
    if not server_exists:
        print(f"Server '{server_name}' not found, registering...")
        server_id = await client.register_server_with_router(server_name)
        if not server_id:
            print(f"Failed to register server '{server_name}'")
            return None
        
        print(f"Server '{server_name}' registered with ID: {server_id}")
        
        # Start the server
        started = await client.start_server_in_router(server_name)
        if not started:
            print(f"Failed to start server '{server_name}'")
            return None
        
        print(f"Server '{server_name}' started successfully")
    
    return server_id


async def list_server_tools(client: MCPClient, server_name: str) -> List[Dict[str, Any]]:
    """List all tools available on a server.
    
    Args:
        client: The MCPClient with Router configuration.
        server_name: The name of the server.
        
    Returns:
        List of tool information dictionaries.
    """
    # Create a session for the server
    session = await client.create_session(server_name, auto_register=True)
    
    # Get the tools
    tools = session.tools
    
    # Close the session
    await client.close_session(server_name)
    
    return tools


async def main():
    """Run the example."""
    # Create MCPClient with Router configuration
    client = MCPClient(config=CONFIG)

    try:
        # Process each server in the configuration
        for server_name in client.get_server_names():
            print(f"\nProcessing server: {server_name}")
            
            # Ensure the server is running
            server_id = await ensure_server_running(client, server_name)
            if not server_id:
                print(f"Skipping server '{server_name}' due to startup failure")
                continue
            
            # List the tools on the server
            print(f"Listing tools for server '{server_name}':")
            tools = await list_server_tools(client, server_name)
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
        
        # Demonstrate creating a session with auto-registration
        print("\nCreating session for puppeteer server with auto-registration:")
        puppeteer_session = await client.create_session(
            "puppeteer", 
            auto_initialize=True,
            auto_register=True
        )
        
        print(f"Puppeteer session created with {len(puppeteer_session.tools)} tools")
        
        # Call a browser tool
        print("\nNavigating to example.com...")
        result = await puppeteer_session.call_tool(
            "browser.navigate", 
            {"url": "https://www.example.com"}
        )
        print(f"Navigation result: {result}")
        
        # Take a screenshot
        print("Taking a screenshot...")
        screenshot_result = await puppeteer_session.call_tool(
            "browser.screenshot", 
            {}
        )
        print(f"Screenshot result: {screenshot_result}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Ensure all sessions are closed
        await client.close_all_sessions()
        print("\nAll sessions closed")


if __name__ == "__main__":
    asyncio.run(main())
