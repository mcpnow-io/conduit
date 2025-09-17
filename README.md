# Conduit - The MCP Server for Phabricator and Phorge
Conduit is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) server that provides seamless integration with Phabricator and Phorge APIs, enabling advanced automation and interaction capabilities for developers and tools.

## Conduit
**Modern HTTP Client**: Built with `httpx` for HTTP/2 support and better performance

**MCP Integration**: Ready-to-use MCP tools for task management

**Type Safety**: Full type hints for better development experience

**Secure**: Token-based authentication with environment variable configuration

## Usage
### Via `uvx`
You need to install `uv` first. If it is not installed, run the following command:
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```
After installation, restart your shell or terminal to apply the environment variable changes.

Then run:
```sh
uvx --from git+https://github.com/mcpnow-io/conduit conduit-mcp
```

### From Source
To install from source for development or contribution:

```sh
# Clone the repository
git clone https://github.com/mcpnow-io/conduit.git
cd conduit

# Install in development mode with all dependencies
pip install -e .[dev]
```

This will install the package in editable mode with all development dependencies.

### Docker
We are still working on Docker support. We estimate it will be available soon.

### As HTTP/SSE Server
Conduit can run as an HTTP/SSE server for multi-user scenarios. This mode allows multiple clients to connect simultaneously, each using their own authentication tokens.

```sh
conduit-mcp --host 127.0.0.1 --port 8000
```
When running as an HTTP server, authentication tokens are provided via HTTP headers instead of environment variables.

```
X-PHABRICATOR-TOKEN: your-32-character-token-here
```

## Configuration
Before running the server, you need to set up the following environment variables:

### Environment Variables
```sh
export PHABRICATOR_TOKEN=your-api-token-here
export PHABRICATOR_URL="https://your-phabricator-instance.com/api/"

export PHABRICATOR_PROXY="socks5://127.0.0.1:1080"  # Optional, if your network is behind a firewall
export PHABRICATOR_DISABLE_CERT_VERIFY=1  # Optional, if your network is under HTTPS filter (WARNING: Disabling certificate verification can expose you to security risks. Only set this if you trust your network environment.)
```
Do note that in HTTPS/SSE mode, `PHABRICATOR_TOKEN` is NOT needed.

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

If you are interested in fixing issues and contributing directly to the code base, please see the document [How to Contribute](https://github.com/mcpnow-io/conduit/wiki/How-to-Contribute)：
* [First-Time Setup](https://github.com/mcpnow-io/conduit/wiki/How-to-Contribute#first-time-setup) - Now uses modern `pyproject.toml` for dependency management
* [Submitting a Pull Request](https://github.com/mcpnow-io/conduit/wiki/How-to-Contribute#submitting-a-pull-request)
* [Running Unittests](https://github.com/mcpnow-io/conduit/wiki/How-to-Contribute#running-unittests)

### Development Setup
This project uses modern Python packaging with `pyproject.toml` for dependency management and build configuration. To set up for development:

1. Install the package in editable mode with development dependencies:
   ```sh
   pip install -e .[dev]
   ```

2. Run pre-commit hooks to ensure code quality:
   ```sh
   pre-commit run -a
   ```

3. Run tests with coverage:
   ```sh
   coverage run -m pytest -s
   ```

## License
Copyright (c) 2025 mpcnow.io. All rights reserved.

Licensed under the [MIT](LICENSE) license.
