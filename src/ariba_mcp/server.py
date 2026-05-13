import os

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_settings
from ariba_mcp.prompts import register_all_prompts
from ariba_mcp.tools import register_all_tools

_client = AribaClient(get_settings())

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

register_all_tools(mcp, _client)
register_all_prompts(mcp)

if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport in ("http", "sse", "streamable-http"):
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        mcp.run(transport=transport, host=host, port=port)
    else:
        mcp.run()
