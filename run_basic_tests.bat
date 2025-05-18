@echo off
REM Run basic integration tests for MCP Router

echo Running basic integration tests...
echo NOTE: Make sure to set up a .env file based on .env.example with your auth token
pytest tests/integration/test_basic_integration.py -v
