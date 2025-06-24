# Conduit - The MCP Server for Phabricator and Phorge
Conduit is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) server that provides seamless integration with Phabricator and Phorge APIs, enabling advanced automation and interaction capabilities for developers and tools.

## Conduit
**Modern HTTP Client**: Built with `httpx` for HTTP/2 support and better performance

**Sync & Async**: Both synchronous and asynchronous API clients

**MCP Integration**: Ready-to-use MCP tools for task management

**Type Safety**: Full type hints for better development experience

**Secure**: Token-based authentication with environment variable configuration

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

## Contributing
There are many ways in which you can participate in this project, for example:
* Submit [bugs and feature requests](https://github.com/mcpnow-io/conduit/issues), and help us verify as they are checked in
* Review [source code changes](https://github.com/mcpnow-io/conduit/pulls)
* Review the [wiki](https://github.com/mcpnow-io/conduit/wiki) and make pull requests for anything from typos to additional and new content

If you are interested in fixing issues and contributing directly to the code base, please see the document [How to Contribute](https://github.com/mcpnow-io/conduit/wiki/How-to-Contribute)，其中涵盖以下内容：
* [First-Time Setup](https://github.com/mcpnow-io/conduit/wiki/How-to-Contribute#first-time-setup)
* [Submitting a Pull Request](https://github.com/mcpnow-io/conduit/wiki/How-to-Contribute#submitting-a-pull-request)
* [Running Unittests](https://github.com/mcpnow-io/conduit/wiki/How-to-Contribute#running-unittests)

## License
Copyright (c) 2025 mpcnow.io. All rights reserved.

Licensed under the [MIT](LICENSE) license.
