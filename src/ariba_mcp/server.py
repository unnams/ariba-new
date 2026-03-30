"""SAP Ariba MCP Server — entrypoint.

API Reference: https://help.sap.com/docs/ariba-apis
Developer Portal: https://developer.ariba.com
"""

import httpx
from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_settings
from ariba_mcp.tools import register_all_tools

# Create shared client at module level so tools are registered at import time.
# The httpx.AsyncClient is created per-request inside AribaClient methods.
_settings = get_settings()
_http_client = httpx.AsyncClient()
_ariba_client = AribaClient(_settings, _http_client)

mcp = FastMCP(
    "ariba-mcp",
    instructions=(
        "SAP Ariba Procurement MCP Server. "
        "Use ariba_* tools to query procurement reporting, sourcing projects, "
        "analytical data, supplier information, contract compliance, "
        "document approvals, audit logs, and supplier risk from your SAP Ariba realm. "
        "API docs: https://help.sap.com/docs/ariba-apis"
    ),
)

# Register all tools at import time so they show up in tools/list
register_all_tools(mcp, _ariba_client)

if __name__ == "__main__":
    mcp.run()
