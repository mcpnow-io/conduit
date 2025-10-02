# Conduit MCP Server - AI Development Guide

## Architecture Overview

Conduit is a Model Context Protocol (MCP) server that provides seamless integration with Phabricator and Phorge APIs. The architecture follows a modular client pattern with unified entry points.

### Core Components
- **Main Server** (`src/conduit.py`): FastMCP-based server with dual transport modes (stdio/HTTP-SSE)
- **Unified Client** (`src/client/unified.py`): Main client with enhanced features (caching, retries, token optimization)
- **Modular Clients** (`src/client/*.py`): Specialized clients for different Phabricator APIs (maniphest, differential, diffusion, etc.)

### Supported API Modules
- **Maniphest** (`maniphest.py`): Task management - search, create, and edit tasks
- **Differential** (`differential.py`): Code review - search, create, and manage differential revisions
- **Diffusion** (`diffusion.py`): Repository management - search repositories, browse code, get commit information
- **File** (`file.py`): File management - search, upload, and download files
- **User** (`user.py`): User management - get user information, query user details
- **Project** (`project.py`): Project management - search projects, manage project members
- **Conduit** (`misc.py`): System interface - ping, get server capabilities, system information

### Transport Modes
- **Stdio Mode**: Single-user, token from `PHABRICATOR_TOKEN` environment variable
- **HTTP/SSE Mode**: Multi-user, token from `X-PHABRICATOR-TOKEN` header, use `--host/--port` flags

## Development Workflow

### Environment Setup
```bash
# Development installation
pip install -e .[dev]

# Required environment variables
export PHABRICATOR_TOKEN="your-32-character-token"
export PHABRICATOR_URL="https://your-phabricator-instance.com/api/"
export PHABRICATOR_PROXY="socks5://127.0.0.1:1080"  # Optional
export PHABRICATOR_DISABLE_CERT_VERIFY=1  # Optional (security risk)
```

### Testing
```bash
# Run all tests with coverage
coverage run -m pytest -s

# Pre-commit hooks (includes flake8, bandit security scan)
pre-commit run -a

# Integration testing requires Docker environment
cd tests/ && docker build -t phorge_debug .
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
- Use type-safe transaction objects from `src.client.types` for updates
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
- TypedDict definitions for all API responses in `src.client/types.py`
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

## Performance Considerations

- Enable caching for read-heavy operations (`enable_cache=True`)
- Use token optimization for large search results
- Configure appropriate timeouts for network conditions
- Monitor connection pool usage in high-concurrency scenarios