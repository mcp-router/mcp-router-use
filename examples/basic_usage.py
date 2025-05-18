"""
Basic usage example for mcp-router-use.

This example demonstrates how to use the MCP Router SDK to
interact with a Puppeteer MCP server.
"""

import asyncio
import logging
import os
from mcp_router_use import MCPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Sample configuration with MCP Router and server details
CONFIG = {
    "mcpRouter": {
        "router_url": "http://localhost:3282",  # Default MCP Router URL
    },
    "mcpServers": {
        "puppeteer": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
            "env": {
                "PUPPETEER_LAUNCH_OPTIONS": "{ \"headless\": true }"
            }
        }
    }
}


async def main():
    # Create client with our configuration
    client = MCPClient(CONFIG)
    
    try:
        # Create a session with the Puppeteer server
        print("Creating session with Puppeteer server...")
        session = await client.create_session("puppeteer", auto_register=True)
        
        # Check available tools
        print("Available tools:")
        for tool in session.tools:
            print(f"  - {tool.name}")
            
        # Navigate to a URL
        print("Navigating to example.com...")
        result = await session.call_tool("browser.navigate", {"url": "https://example.com"})
        print(f"Navigation result: {result}")
        
        # Take a screenshot (if available)
        if any(tool.name == "browser.screenshot" for tool in session.tools):
            print("Taking screenshot...")
            screenshot_result = await session.call_tool("browser.screenshot", {})
            
            # Save the screenshot
            if "resourceUri" in screenshot_result:
                # Read the screenshot resource
                content, mime_type = await session.connector.read_resource(
                    screenshot_result["resourceUri"]
                )
                
                # Save to file
                os.makedirs("screenshots", exist_ok=True)
                with open("screenshots/example.png", "wb") as f:
                    f.write(content)
                print("Screenshot saved to screenshots/example.png")
                
        # Get page title
        print("Getting page title...")
        eval_result = await session.call_tool("browser.evaluate", {"expression": "document.title"})
        print(f"Page title: {eval_result}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        # Close all sessions
        await client.close_all_sessions()
        
if __name__ == "__main__":
    asyncio.run(main())
