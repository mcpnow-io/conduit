# Conduit - The MCP Server for Phabricator and Phorge
Conduit is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) server that provides seamless integration with Phabricator and Phorge APIs, enabling advanced automation and interaction capabilities for developers and tools.

## Features

**Modern HTTP Client**: Built with `httpx` for HTTP/2 support and better performance
**Sync & Async**: Both synchronous and asynchronous API clients
**MCP Integration**: Ready-to-use MCP tools for task management
**Type Safety**: Full type hints for better development experience
**Secure**: Token-based authentication with environment variable configuration

## Use Cases
* Automating your workflows and processes.
* Building AI powered tools and applications that interact with your organization's Phabricator/Phorge.
* Batch operations on tasks, projects, and users.
* Integration with modern async Python applications.

## Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables (see Configuration section)
4. Run the server: `python src/conduit.py`

## Configuration
Before running the server, you need to set up the following environment variables:

### Required Environment Variables

```bash
# Your Phabricator API token (32 characters)
export PHABRICATOR_TOKEN=your-api-token-here

# Your Phabricator API URL
export PHABRICATOR_URL=https://your-phabricator-instance.com/api/
```

### Getting Your API Token
1. Log into your Phabricator instance
2. Go to Settings > API Tokens
3. Generate a new token
4. Copy the 32-character token and use it as `PHABRICATOR_TOKEN`

### Configuration File
You can also copy `.env.example` to `.env` and set your values there:

```bash
cp .env.example .env
# Edit .env with your actual values
```

## Quick Start

### Using the Client Directly

```python
from src.client import PhabricatorClient

# Synchronous usage
with PhabricatorClient(api_url, api_token) as client:
    # Test connection
    user = client.test_connection()
    print(f"Connected as: {user['userName']}")

    # Create a task
    task = client.create_task(
        title="Fix login issue",
        description="Users can't log in...",
        priority="high"
    )
```

### Async Usage

```python
import asyncio
from src.client import AsyncPhabricatorClient

async def main():
    async with AsyncPhabricatorClient(api_url, api_token) as client:
        user_info = await client.test_connection()
        tasks = await client.search_tasks(limit=10)
        print(f"Found {len(tasks['data'])} tasks")

asyncio.run(main())
```

## Tools

The MCP server provides the following tools:

### `create_phabricator_task`
Create a new Phabricator task.

**Parameters:**
- `title` (string): The title of the task
- `description` (string, optional): Task description with Phabricator Markdown support
- `owner_phid` (string, optional): Owner PHID (e.g., "PHID-USER-xxxxx")

### `search_phabricator_tasks`
Search for existing tasks.

**Parameters:**
- `query` (string, optional): Search query for titles/descriptions
- `status` (string, optional): Filter by status ('open', 'resolved', 'wontfix', etc.)
- `limit` (integer, optional): Maximum results (default: 20, max: 100)

### `get_phabricator_task`
Get details of a specific task.

**Parameters:**
- `task_id` (integer): The ID of the task to retrieve

### `test_phabricator_connection`
Test the API connection and get current user information.

## Development

### Testing the Client

Run the test script to verify your setup:

```bash
python test_client.py
```

### Using the Development Server

For development with hot reloading:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install
pre-commit run --all-files

# Run tests
pytest
```

## Documentation

- [Usage Examples](USAGE.md) - Detailed usage examples and patterns
- [API Documentation](src/client/client.py) - Full API reference in docstrings

## Dependencies

- `httpx` - Modern HTTP client with HTTP/2 support
- `fastmcp` - Model Context Protocol server framework
- `python-dotenv` - Environment variable management

## License
This project is licensed under the terms of the MIT open source license. Please refer to [MIT](./LICENSE) for the full terms.
