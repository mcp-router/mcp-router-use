"""
Example using the MCP Router Use SDK.

This example demonstrates how to use the SDK to connect to MCP servers
through MCP Router with auto-registration and auto-starting capabilities.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any

from mcp_router_use import MCPClient, MCPRouterClient, set_debug

# Set debug level (0: no debug, 1: info, 2: debug)
set_debug(2)


async def basic_example():
    """Basic usage example with MCPClient."""
    print("\n== Running Basic Example with MCPClient ==")
    
    # Create configuration for MCP Router
    config = {
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
            }
        }
    }

    # Create MCPClient with Router configuration
    client = MCPClient(config=config)

    try:
        # Create a session with auto-registration
        print("Creating session with auto-registration...")
        session = await client.create_session("puppeteer", auto_register=True)
        print(f"Session initialized with {len(session.tools)} tools")

        # List available tools
        for i, tool in enumerate(session.tools):
            print(f"{i+1}. Tool: {tool['name']} - {tool['description']}")

        # Call a tool (example: browser.navigate)
        print("\nNavigating to example.com...")
        result = await session.call_tool(
            "browser.navigate", 
            {"url": "https://www.example.com"}
        )
        print(f"Navigation result: {json.dumps(result, indent=2)}")

        # Get a screenshot
        print("\nTaking a screenshot...")
        screenshot_result = await session.call_tool(
            "browser.screenshot", 
            {}
        )
        print(f"Screenshot taken (data length: {len(screenshot_result.get('image', ''))} bytes)")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Disconnect session
        await session.disconnect()
        print("Session disconnected")


async def router_client_example():
    """Example using the specialized MCPRouterClient."""
    print("\n== Running Example with MCPRouterClient ==")
    
    # Create configuration for MCP Router
    config = {
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
            }
        }
    }

    # Create MCPRouterClient with configuration
    client = MCPRouterClient(config=config)

    try:
        # Get list of available servers from the router
        print("Getting available servers from MCP Router...")
        servers = await client.get_router_servers()
        print(f"Found {len(servers)} servers in MCP Router")
        for i, server in enumerate(servers):
            print(f"{i+1}. {server.get('name', 'Unknown')} - Status: {server.get('status', 'Unknown')}")
            
        # Create a session (auto-register is True by default in MCPRouterClient)
        print("\nCreating session...")
        session = await client.create_session("puppeteer")
        print(f"Session initialized with {len(session.tools)} tools")

        # List available tools
        print("\nAvailable tools:")
        for i, tool in enumerate(session.tools):
            print(f"{i+1}. Tool: {tool['name']} - {tool['description']}")

        # Call a tool (example: browser.navigate)
        print("\nNavigating to example.com...")
        result = await session.call_tool(
            "browser.navigate", 
            {"url": "https://www.example.com"}
        )
        print(f"Navigation result: {json.dumps(result, indent=2)}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Disconnect session
        await session.disconnect()
        print("Session disconnected")


async def main():
    """Run all examples."""
    # Run the basic example
    await basic_example()
    
    # Run the router client example
    await router_client_example()


if __name__ == "__main__":
    asyncio.run(main())
