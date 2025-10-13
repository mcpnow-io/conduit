# Conduit MCP Server - AI Development Guide

## Architecture Overview

Conduit is a Model Context Protocol (MCP) server that provides seamless integration with Phabricator and Phorge APIs through a modular client pattern with unified entry points.

### Core Architecture
- **Main Server** (`src/conduit.py`): FastMCP-based server with dual transport modes (stdio/HTTP-SSE)
- **Unified Client** (`src/client/unified.py`): Enhanced client with caching, retries, and token optimization
- **Modular Clients** (`src/client/*.py`): Specialized clients for different Phabricator APIs

### Supported APIs
- **Maniphest**: Task management (search, create, edit tasks)
- **Differential**: Code review (search, create, manage revisions)
- **Diffusion**: Repository management (search, browse, commits)
- **File**: File management (search, upload, download)
- **User**: User management (information, queries)
- **Project**: Project management (search, members, workboards)
- **Conduit**: System interface (ping, capabilities, info)

## Development Workflow

### Environment Setup

This project uses `uv` virtual environment. Before executing any Python code, activate the Python virtual environment first:
```bash
# Since this is a Phabricator MCP Server, you may set environment variables
# Example environment variables (replace with your actual values):
# export PHABRICATOR_TOKEN="your-32-character-token"
# export PHABRICATOR_URL="https://your-phabricator-instance.com/api/"
# export PHABRICATOR_PROXY="socks5://127.0.0.1:1080"  # Optional
# export PHABRICATOR_DISABLE_CERT_VERIFY=1  # Optional (security risk)

# Actual execution with environment variables:
PHABRICATOR_TOKEN="your-32-character-token" \
PHABRICATOR_URL="https://your-phabricator-instance.com/api/" \
PHABRICATOR_PROXY="socks5://127.0.0.1:1080" \
PHABRICATOR_DISABLE_CERT_VERIFY=1 \
source venv/bin/activate && python your_script.py

# Example, actual name may changed
source venv/bin/activate && uv pip xxx
source xxx && python xxx
```

### MCP Server Execution Modes

The Conduit MCP Server supports two execution modes:

#### 1. Stdio Mode (Default)
- **Required**: `PHABRICATOR_TOKEN`, `PHABRICATOR_URL`
- **Run**: `python run.py`

#### 2. HTTP/SSE Mode
- **Required**: `PHABRICATOR_URL` only
- **Token**: Provided via HTTP header `X-PHABRICATOR-TOKEN`
- **Run**: `python run.py --host 127.0.0.1 --port 8000`

### Testing
To run unittests, you need to install Docker on your environment to run Phorge in the background.
```bash
cd tests
docker build -t phorge_debug .
docker run -d --rm -p 8080:80 --name phorge_debug phorge_debug
```
Use `docker ps` to determine whether the user has run the phorge image already. The phorge_debug container will automatically initialize the Phorge environment, enable username/password authorization, and generate a User API key for the default admin user with password `Passw0rd`. By default, you can access your locally running Phorge instance at http://127.0.0.1:8080/.

You can retrieve the User API Key by entering the following command:
```bash
docker exec phorge_debug /usr/local/bin/get-api-token.sh
```

Before executing any Python code or command, you need to activate the Python virtual environment first. Use `source xxx/bin/activate` to activate venv. After that, you can run unittest (or any Python command) locally by this command:
```bash
PHABRICATOR_TOKEN=<api-token> PHABRICATOR_URL=http://127.0.0.1:8080/api/ pytest # or any Python command
```

### Code Quality Tools
- **Security**: bandit scanning (`.bandit_scan.cfg`)
- **Pre-commit**: Automated quality checks (`.pre-commit-config.yaml`)

## API Patterns

### Client Usage Patterns
```python
# Basic client (backward compatible)
client = PhabricatorClient(api_url, api_token)

# Enhanced client with caching/retries
client = PhabricatorClient(
    api_url, api_token,
    timeout=60.0,
    max_retries=5,
    enable_cache=True,
    cache_ttl=600
)

# Access specialized modules
tasks = client.maniphest.search_tasks(constraints={"statuses": ["open"]})
diffs = client.differential.search_revisions(author_phids=[user_phid])
```

### MCP Tool Development
- All tools use `@handle_api_errors` decorator for structured error responses
- Apply `@optimize_token_usage` for search results that may return large datasets
- Use type-safe transaction objects from `conduit.client.types` for updates
- Follow naming convention: `pha_<module>_<action>` (e.g., `pha_task_search_advanced`)

### Error Handling
```python
# Structured error responses
{
    "success": False,
    "error": "Authentication failed: Invalid API token",
    "error_code": "AUTH_ERROR",
    "suggestion": "Verify your PHABRICATOR_TOKEN environment variable"
}
```

## Key Conventions

### Token Optimization
- Smart pagination automatically limits results (default 100 items)
- Token budget optimization with `max_tokens` parameter
- Response truncation with guidance for large text content

### Type Safety
- Optional runtime validation via `enable_type_safety` parameter
- TypedDict definitions for all API responses in `conduit.client/types.py`
- Validation decorators for function signatures

### Transaction Pattern
```python
# Use transaction objects for updates
transactions = [
    ManiphestTaskTransactionTitle(type="title", value=new_title),
    ManiphestTaskTransactionStatus(type="status", value="open")
]
client.maniphest.edit_task(task_id, transactions)
```

### Configuration Management
- Environment-based configuration via `PhabricatorConfig` class
- Token validation (must be exactly 32 characters)
- URL normalization (adds trailing slash if missing)

## Critical Integration Points

### Docker Test Environment
- Uses Phorge (Phabricator fork) in Docker for integration tests
- Bootstrap script creates admin user and generates API token
- Test database setup with MySQL

### FastMCP Integration
- Tool registration in `register_tools()` function
- Context managers for client lifecycle
- Error boundary handling with structured responses

### HTTP Client Configuration
- httpx with HTTP/2 support and connection pooling
- Configurable timeouts, retries, and proxy support
- Certificate verification control for corporate environments

## File Structure Guidelines

- **Client Modules**: One per Phabricator API (maniphest.py, differential.py, etc.)
- **Type Definitions**: Centralized in `src/client/types.py`
- **Utilities**: Shared functionality in `src/utils/` (errors, validation, parameters)
- **Tools**: MCP tool definitions in `src/main_tools.py`
- **Tests**: Mirror source structure in `src/client/tests/`

## Common Pitfalls

1. **Token Format**: API tokens must be exactly 32 characters
2. **URL Format**: Must end with `/` and start with `http://` or `https://`
3. **Pagination**: Always handle cursor-based pagination for large result sets
4. **Error Codes**: Use structured error responses, not raw exceptions
5. **Type Safety**: Runtime validation is optional - check `enable_type_safety` parameter

## FastMCP Debugging Guide

### List MCP Tools
```python
import asyncio
from fastmcp import FastMCP

async def list_tools():
    mcp = FastMCP('test')
    # Register tools first
    register_tools(mcp, get_client_func)
    
    tools = await mcp.get_tools()
    print(f"Total tools: {len(tools)}")
    print("Tool names:", list(tools.keys()))

asyncio.run(list_tools())
```

### Debug Tool Registration
```python
# Check specific tool
tools = await mcp.get_tools()
if 'pha_project_search' in tools:
    tool = tools['pha_project_search']
    print(f"Tool: {tool.name}")
    print(f"Description: {tool.description}")
```

### FastMCP Key Points
- `mcp.get_tools()` returns dict with tool names as keys
- Tools must be defined inside `register_tools()` function
- Use `@mcp.tool()` decorator to expose functions
- Error handling with `@handle_api_errors` decorator