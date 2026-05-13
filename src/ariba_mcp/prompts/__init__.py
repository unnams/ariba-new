"""MCP Prompts ("skills") for ariba-mcp.

Each module registers one or more `@mcp.prompt(...)` functions on the FastMCP
server. Prompts appear in MCP clients (Claude Desktop, Claude Code, etc.) as
slash commands and orchestrate the underlying ariba_* tools.
"""

from fastmcp import FastMCP

from ariba_mcp.prompts import procurement

_MODULES = [procurement]


def register_all_prompts(mcp: FastMCP) -> None:
    """Register prompts from every module."""
    for m in _MODULES:
        m.register(mcp)
