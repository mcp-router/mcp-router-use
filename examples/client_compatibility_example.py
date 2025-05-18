"""
Example demonstrating MCPClient usage with and without MCP Router.

This example shows how to use MCPClient with and without MCP Router configuration.
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from mcp_router_use import MCPAgent, MCPClient, set_debug

# Set debug level for detailed output
set_debug(2)


async def run_with_router():
    """Run example with MCP Router configuration."""
    print("Running with MCP Router...")
    
    # Create configuration dictionary with router settings
    config = {
        "mcpRouter": {
            "router_url": "http://localhost:3282",
        },
        "mcpServers": {
            "puppeteer": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
                "env": {
                    "PUPPETEER_LAUNCH_OPTIONS": "{ \"headless\": false }"
                }
            }
        }
    }

    # Create MCPClient with Router configuration
    client = MCPClient(config=config)

    try:
        # Create a session with auto-registration
        session = await client.create_session(
            "puppeteer", 
            auto_initialize=True,
            auto_register=True  # This parameter registers and starts the server if needed
        )
        print(f"Session created with {len(session.tools)} tools")

        # Close the session
        await client.close_session("puppeteer")
        print("Session closed")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close_all_sessions()


async def run_with_agent():
    """Run example using MCPAgent with MCPClient."""
    print("\nRunning with MCPAgent...")
    
    # Load environment variables for OpenAI API key
    load_dotenv()
    
    # Create configuration with router
    config = {
        "mcpRouter": {
            "router_url": "http://localhost:3282",
        },
        "mcpServers": {
            "puppeteer": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
                "env": {
                    "PUPPETEER_LAUNCH_OPTIONS": "{ \"headless\": false }"
                }
            }
        }
    }

    # Create MCPClient
    client = MCPClient(config=config)
    
    # Create LLM
    llm = ChatOpenAI(model="gpt-4o")
    
    try:
        # Create MCPAgent
        agent = MCPAgent(llm=llm, client=client, max_steps=30)
        
        # Run query 
        result = await agent.run(
            "Navigate to example.com and tell me the title of the page",
            server_name="puppeteer"  # Specify server name
        )
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close_all_sessions()


async def run_with_multiple_servers():
    """Run example with multiple servers through MCP Router."""
    print("\nRunning with multiple servers...")
    
    # Configuration with multiple servers
    config = {
        "mcpRouter": {
            "router_url": "http://localhost:3282",
        },
        "mcpServers": {
            "puppeteer": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
                "env": {
                    "PUPPETEER_LAUNCH_OPTIONS": "{ \"headless\": false }"
                }
            },
            "web-search": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-web-search"],
                "env": {
                    "API_KEY": "your_api_key_here"  # Replace with your actual API key
                }
            }
        }
    }

    # Create MCPClient with multiple servers
    client = MCPClient(config=config)

    try:
        # Register and start all servers automatically
        servers = client.get_server_names()
        for server_name in servers:
            print(f"Creating session for {server_name}...")
            session = await client.create_session(server_name, auto_register=True)
            print(f"Session for {server_name} created with {len(session.tools)} tools")
            
            # Close the session when done
            await client.close_session(server_name)
            print(f"Session for {server_name} closed")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close_all_sessions()


async def main():
    """Run all examples."""
    await run_with_router()
    await run_with_agent()
    await run_with_multiple_servers()


if __name__ == "__main__":
    asyncio.run(main())
