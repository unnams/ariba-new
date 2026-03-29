"""SAP Ariba MCP Server — entrypoint.

Exposes 35+ tools across 8 SAP Ariba API domains:
- Operational Reporting for Procurement
- Operational Reporting for Strategic Sourcing
- Analytical Reporting
- Supplier Data & Profiles
- Contract Compliance & Workspaces
- Sourcing Project Management
- Document Approval & Audit
- Supplier Risk

API Reference: https://help.sap.com/docs/ariba-apis
Developer Portal: https://developer.ariba.com
"""

from contextlib import asynccontextmanager

import httpx
from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_settings
from ariba_mcp.tools import register_all_tools


@asynccontextmanager
async def lifespan(server: FastMCP):
    """Manage the shared AribaClient lifecycle."""
    settings = get_settings()
    async with httpx.AsyncClient() as http_client:
        client = AribaClient(settings, http_client)
        register_all_tools(server, client)
        yield {"client": client}


mcp = FastMCP(
    "ariba-mcp",
    instructions=(
        "SAP Ariba Procurement MCP Server. "
        "Use ariba_* tools to query procurement reporting, sourcing projects, "
        "analytical data, supplier information, contract compliance, "
        "document approvals, audit logs, and supplier risk from your SAP Ariba realm. "
        "API docs: https://help.sap.com/docs/ariba-apis"
    ),
    json_response=True,
    lifespan=lifespan,
)

if __name__ == "__main__":
    mcp.run()
