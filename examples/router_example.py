"""
Example usage of MCP Router integration.

This example demonstrates how to use the MCPClient to manage MCP servers
through MCP Router, including registration and auto-starting.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any

from mcp_router_use import MCPClient, set_debug

# Set debug level (0: no debug, 1: info, 2: debug)
set_debug(2)


async def main():
    """Run the example."""
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
        # Register and start the server
        server_id = await client.register_server_with_router("puppeteer")
        if not server_id:
            print("Failed to register server")
            return

        print(f"Server registered with ID: {server_id}")

        # Start the server
        started = await client.start_server_in_router("puppeteer")
        if not started:
            print("Failed to start server")
            return

        print("Server started successfully")

        # Create a session
        session = await client.create_session("puppeteer")
        print(f"Session initialized with {len(session.tools)} tools")

        # List available tools
        for tool in session.tools:
            print(f"Tool: {tool.name} - {tool.description}")

        # Call a tool (example: browser.navigate)
        result = await session.call_tool(
            "browser.navigate", 
            {"url": "https://www.example.com"}
        )
        print(f"Navigation result: {result}")

        # Get a screenshot
        screenshot_result = await session.call_tool(
            "browser.screenshot", 
            {}
        )
        print(f"Screenshot taken: {screenshot_result}")

        # Close the session
        await client.close_session("puppeteer")
        print("Session closed")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Ensure all sessions are closed
        await client.close_all_sessions()


if __name__ == "__main__":
    asyncio.run(main())
