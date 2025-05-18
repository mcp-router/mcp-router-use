# MCP Router Use

SDK for managing and using MCP servers through MCP Router.

## Overview

MCP Router Use is a Python SDK that allows you to interact with MCP servers through the MCP Router. It provides a simplified interface for:

- Registering MCP servers with MCP Router
- Starting and stopping MCP servers
- Creating sessions to communicate with MCP servers
- Calling tools exposed by MCP servers

The SDK handles the complexities of server management, allowing you to focus on using the MCP tools.

## Installation

```bash
pip install mcp-router-use
```

## Configuration

### Configuration Object

To use the SDK, you need to create a configuration object that specifies:

1. The MCP Router URL and authentication details
2. The MCP servers you want to use

Here's an example configuration:

```python
config = {
    "mcpRouter": {
        "router_url": "http://localhost:3282",
        "auth_token": "your_token_here",  # Optional
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
```

### Using .env for Authentication

For security, it's recommended to store your authentication token in a `.env` file instead of hardcoding it in your code:

1. Create a `.env` file in your project root based on the provided `.env.example`:
   ```
   # MCP Router authentication token
   MCP_ROUTER_AUTH_TOKEN=your_token_here
   
   # Optional: MCP Router URL (default: http://localhost:3282)
   # MCP_ROUTER_URL=http://localhost:3282
   ```

2. Load the environment variables in your code:
   ```python
   import os
   from dotenv import load_dotenv
   
   # Load variables from .env
   load_dotenv()
   
   # Create config using environment variables
   config = {
       "mcpRouter": {
           "router_url": os.environ.get("MCP_ROUTER_URL", "http://localhost:3282"),
           "auth_token": os.environ.get("MCP_ROUTER_AUTH_TOKEN"),
       },
       # ...rest of your config
   }
   ```

## Usage

### Basic Usage

```python
import asyncio
from mcp_router_use import MCPClient

async def main():
    # Create a client with your configuration
    client = MCPClient(config=config)
    
    # Create a session with auto-registration
    session = await client.create_session("puppeteer", auto_register=True)
    
    # Call a tool
    result = await session.call_tool("browser.navigate", {"url": "https://www.example.com"})
    
    # Disconnect when done
    await session.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### Loading Configuration from a File

You can also load your configuration from a JSON file:

```python
import asyncio
from mcp_router_use import MCPClient

async def main():
    # Load configuration from a file
    client = MCPClient(config="config.json")
    
    # Use the client as before
    session = await client.create_session("puppeteer", auto_register=True)
    
    # ...

if __name__ == "__main__":
    asyncio.run(main())
```

## Running Tests

### Unit Tests

To run the unit tests:

```bash
pytest tests/unit
```

### Integration Tests

To run the integration tests, you need to have MCP Router running on http://localhost:3282.

**Important:** For integration tests, you'll need to set up your authentication token:

1. Copy the `.env.example` file to `.env` in the project root:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to set your MCP Router authentication token:
   ```
   MCP_ROUTER_AUTH_TOKEN=your_actual_token_here
   ```

3. Run the integration tests:
   ```bash
   # Run basic integration tests
   pytest tests/integration/test_basic_integration.py -v

   # Or use the convenience script
   ./run_basic_tests.sh  # Linux/macOS
   run_basic_tests.bat   # Windows
   ```

The integration tests check basic connectivity to the MCP Router's `/mcp` endpoint. They will automatically use the authentication token from your `.env` file.

## API Reference

### MCPClient

The main client class for interacting with MCP Router.

#### Constructor

```python
MCPClient(config: Union[str, Dict[str, Any], None] = None)
```

- `config`: Either a dictionary containing configuration or a path to a JSON config file.

#### Methods

- `async create_session(server_name: str, auto_initialize: bool = True, auto_register: bool = True) -> MCPSession`: 
  Creates a session for the specified server. If `auto_register` is True, registers and starts the server if needed.

- `async register_server_with_router(server_name: str) -> Optional[str]`: 
  Registers a server with the MCP Router and returns the assigned server ID.

- `async start_server_in_router(server_name: str) -> bool`: 
  Starts a registered server in the MCP Router.

- `async get_router_servers() -> List[Dict[str, Any]]`: 
  Gets a list of all servers registered with the MCP Router.

### MCPSession

Represents a session with an MCP server.

#### Methods

- `async connect() -> None`: 
  Connects to the MCP server.

- `async disconnect() -> None`: 
  Disconnects from the MCP server.

- `async initialize() -> dict[str, Any]`: 
  Initializes the session and discovers available tools.

- `async discover_tools() -> list[dict[str, Any]]`: 
  Discovers available tools from the MCP server.

- `async call_tool(name: str, arguments: dict[str, Any]) -> Any`: 
  Calls a tool with the given arguments.

## Troubleshooting

### Common Issues

1. **Connection Error**: Ensure MCP Router is running and accessible at the configured URL.

2. **Authentication Error**: Check if your `auth_token` in the `.env` file is correct and properly configured.

3. **Server Registration Failure**: Make sure the server configuration is correct and the necessary packages are installed.

4. **Server Start Failure**: Check the MCP Router logs for errors during server startup.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
