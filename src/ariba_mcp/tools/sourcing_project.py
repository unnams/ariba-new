"""Sourcing Project Management and Approval APIs for SAP Ariba.

Covers:
- Sourcing Project Management API:                       sourcing-project/v1/prod
- External Approval API for Sourcing & Supplier Mgmt:    sourcing-approval/v2/prod
- Master Data Retrieval API for Sourcing:                 sourcing-masterdata/v1/prod
- Surrogate Bid API:                                      sourcing-surrogate-bid/v1/prod

Docs: https://help.sap.com/docs/ariba-apis
"""

import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

PROJECT_API = "sourcing-project/v1/prod"
APPROVAL_API = "sourcing-approval/v2/prod"
MASTERDATA_API = "sourcing-masterdata/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register Sourcing Project Management tools."""

    @mcp.tool(
        name="ariba_sourcing_get_project",
        description="Get details of a sourcing project by its internal ID (e.g. Doc1234567).",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_project(project_id: str) -> str:
        try:
            result = await client.fetch_resource(PROJECT_API, f"projects/{project_id}")
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_sourcing_get_workspace",
        description=(
            "Get a sourcing approval workspace by its SR number (e.g. SR30406740). "
            "Returns the workspace with approval flow, status, and document details."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_workspace(sr_number: str) -> str:
        try:
            result = await client.fetch_resource(APPROVAL_API, f"Workspace/{sr_number}")
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_sourcing_get_masterdata",
        description=(
            "Retrieve sourcing master data (commodities, regions, departments, etc.) "
            "from the Master Data Retrieval API for Sourcing."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_masterdata(resource_type: str, page_token: str | None = None) -> str:
        try:
            params = {}
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(MASTERDATA_API, resource_type, params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_sourcing_list_events",
        description="List sourcing events (RFPs, RFQs, auctions) for a sourcing project.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_events(project_id: str) -> str:
        try:
            result = await client.fetch_resource(PROJECT_API, f"projects/{project_id}/events")
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)
