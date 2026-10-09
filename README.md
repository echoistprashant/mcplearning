# MCP Learning

A hands-on Python project for learning the **Model Context Protocol (MCP)**: how to build MCP servers, connect clients, use tools, work with different transports, and prepare a server for deployment.

## What is MCP?

MCP is an open protocol that lets an AI application (the **host**) connect to external capabilities through MCP servers. A server can expose:

- **Tools** — actions the client can call, such as searching or processing data.
- **Resources** — data the client can read, such as files or database records.
- **Prompts** — reusable prompt templates offered by a server.

An MCP **client** runs inside or on behalf of a host, connects to a server, discovers its capabilities, and invokes them. MCP standardizes the communication; it does not itself provide a model or decide which tools are safe to run.

### Transports in this project

- **stdio** — the client starts the server as a child process and communicates over standard input/output. Useful for local tools and desktop integrations.
- **Streamable HTTP** — the server listens on an HTTP endpoint so clients can connect over a network. Useful for remote services and deployments.

## Learning path

| Chapter | Directory | What it demonstrates |
| --- | --- | --- |
| 1. Create an MCP server | [`CH-1-CREATEMCP/`](./CH-1-CREATEMCP/) | Define tools with FastMCP and call them from an MCP SDK client over stdio. |
| 2. HTTP transport | [`CH-2-HTTP_MCP/`](./CH-2-HTTP_MCP/) | Run the same kind of server over Streamable HTTP and connect to its `/mcp` endpoint. |
| 3. Third-party server | [`CH-3-3RDPARTYMCP/`](./CH-3-3RDPARTYMCP/) | Configure a client to launch a community MCP server with `uvx`. |
| 4. Use a PyPI server | [`CH-4_PyPI_MCP/`](./CH-4_PyPI_MCP/) | Install an MCP server package and connect to it using the MCP SDK. |

## Requirements

- Python **3.12 or newer**
- [uv](https://docs.astral.sh/uv/) for creating the environment and installing dependencies
- Internet access for installing packages and running the third-party-server example

## Set up

From the repository root:

```powershell
uv sync
```

This creates or updates `.venv` using `pyproject.toml` and `uv.lock`. Run project commands with `uv run` so they use that environment:

```powershell
uv run python --version
```

## Try the chapters

### 1. Create and call a local stdio server

In one terminal, start the server:

```powershell
uv run python CH-1-CREATEMCP/creatingmcp.py
```

The process waits for an MCP client; that is expected. In a second terminal, run the MCP SDK client:

```powershell
uv run python CH-1-CREATEMCP/python_client.py
```

The client starts the server process, initializes an MCP session, discovers its tools, and calls the `process` tool. The example uses a placeholder path, so replace it with a path meaningful on your machine if needed.

### 2. Run the server over Streamable HTTP

Start the server in one terminal:

```powershell
uv run python CH-2-HTTP_MCP/1_http_mcp.py
```

It listens on port `8050`; the MCP endpoint is:

```text
http://localhost:8050/mcp
```

Leave the server running while a client connects. The included `2_langchain_client.py` demonstrates a LangChain adapter client, but see [Dependency compatibility](#dependency-compatibility) below before running it.

### 3. Connect to a community server

The example client is configured to launch `duckduckgo-mcp-server` with `uvx`, which downloads and runs that package in an isolated tool environment:

```powershell
uv run python CH-3-3RDPARTYMCP/communitymcp.py
```

Review a third-party server's source, publisher, permissions, and package provenance before running it. A server can have access to whatever its tools and execution environment allow.

### 4. Connect to the installed PyPI package

The project dependency list includes `agentic_room`, so `uv sync` installs it in the project environment. The server entry point can also be run directly:

```powershell
uv run python -m agentic_room.main
```

As with the first server, it waits for a client. In another terminal, discover and print its tools:

```powershell
uv run python CH-4_PyPI_MCP/2_client.py
```

That client launches the package using the same Python interpreter as the client. This avoids accidentally using a different Python environment.

## Build your own server

FastMCP turns Python functions into tools. The first chapter's [`creatingmcp.py`](./CH-1-CREATEMCP/creatingmcp.py) is the runnable example:

```python
from fastmcp import FastMCP

mcp = FastMCP("Example")


@mcp.tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

The function name, type hints, and docstring help FastMCP describe the tool to clients. A client can list tools and call one by name with arguments. Keep tool inputs validated and limit each tool to the permissions it needs.

For an HTTP server, change the run configuration:

```python
mcp.run(transport="streamable-http", host="0.0.0.0", port=8050)
```

Binding to `0.0.0.0` makes the service reachable through the machine's network interfaces. Use it only when that is intended; it does not add authentication or encryption.

## Connect to an HTTP server with the MCP SDK

This minimal example uses the MCP SDK directly and avoids a framework adapter:

```python
import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():
    async with streamable_http_client("http://localhost:8050/mcp") as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_tools()

            for tool in result.tools:
                print(tool.name, tool.description)


if __name__ == "__main__":
    asyncio.run(main())
```

For a remote server, replace the URL with its HTTPS MCP endpoint and supply any required authentication according to the server's instructions.

## Deployment concepts

The HTTP chapter is the starting point for deployment:

1. **Choose a host.** Use a machine or container that can run the Python project and reach the network services your tools require.
2. **Start the HTTP server.** Run the server entry point with Streamable HTTP enabled and bind to the container or host interface (`0.0.0.0` inside a container).
3. **Expose the MCP endpoint.** Route external traffic to the server's `/mcp` endpoint. Configure a stable hostname and HTTPS using your hosting platform or a reverse proxy.
4. **Secure it before sharing.** Add authentication and authorization, restrict network access, keep secrets in environment variables or a secret manager, and apply rate and resource limits. Do not assume that knowing the endpoint URL is access control.
5. **Monitor and maintain it.** Capture server logs without leaking credentials or sensitive tool data, monitor failures, pin and update dependencies, and redeploy when code or dependencies change.
6. **Connect a client.** Configure the client with the deployed HTTPS endpoint and the authentication method the service requires.

The repository's HTTP example is for learning and is not a production-ready, authenticated service. In particular, do not expose tools that run shell commands, execute arbitrary Python, write files, or delete files to untrusted users. Review and restrict the tools in any third-party server before deploying it.

## Dependency compatibility

The root project currently depends on `agentic_room`, which requires FastMCP 4 and MCP SDK 2. The installed `langchain-mcp-adapters` release used by the LangChain chapter files expects MCP SDK 1 APIs; importing it with the project's MCP SDK 2 environment can fail with an `ImportError` for `RequestContext`.

The stdio examples in Chapters 1 and 4 use the MCP SDK directly. For adapter-based examples in Chapters 1–3, use a separate environment with a mutually compatible MCP SDK and adapter version, or update those examples to use the MCP SDK directly. Do not downgrade the shared environment's MCP packages without also accounting for `agentic_room`'s FastMCP 4 requirement.

## Project layout

```text
.
├── CH-1-CREATEMCP/       # Build a server and connect over stdio
├── CH-2-HTTP_MCP/        # Streamable HTTP server and client
├── CH-3-3RDPARTYMCP/     # Connect to a community server
├── CH-4_PyPI_MCP/        # Connect to an installed PyPI server
├── pyproject.toml        # Project metadata and dependencies
└── uv.lock               # Reproducible dependency lockfile
```

## Further reading

- [MCP documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP documentation](https://gofastmcp.com/)
- [uv documentation](https://docs.astral.sh/uv/)
- [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters)