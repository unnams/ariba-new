"""Supplier Data APIs for SAP Ariba.

Covers multiple supplier-related APIs:
- Supplier Data API with Pagination: supplier-data/v4/prod
- Supplier Data Extraction API:      supplier-data-extraction/v1/prod
- Ariba Network Supplier Profile API: supplier-profile/v1/prod
- Supplier Information API:           supplier-information/v1/prod

Docs: https://help.sap.com/docs/ariba-apis
"""

import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

SUPPLIER_DATA_API = "supplier-data/v4/prod"
SUPPLIER_PROFILE_API = "supplier-profile/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register Supplier Data tools."""

    @mcp.tool(
        name="ariba_supplier_list",
        description=(
            "List suppliers from the Supplier Data API with pagination. "
            "Returns supplier names, addresses, registration status, qualification status, and preferred status."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_suppliers(page_token: str | None = None) -> str:
        try:
            params = {}
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(SUPPLIER_DATA_API, "suppliers", params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_supplier_get",
        description="Get detailed information for a specific supplier by their supplier ID (ANID or smVendorId).",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_supplier(supplier_id: str) -> str:
        try:
            result = await client.fetch_resource(SUPPLIER_DATA_API, f"suppliers/{supplier_id}")
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_supplier_search",
        description="Search suppliers by name, ID, or qualification status.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def search_suppliers(
        query: str | None = None,
        qualification_status: str | None = None,
        page_token: str | None = None,
    ) -> str:
        try:
            params: dict = {}
            if query:
                params["q"] = query
            if qualification_status:
                params["qualificationStatus"] = qualification_status
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(SUPPLIER_DATA_API, "suppliers", params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_supplier_get_profile",
        description="Get the Ariba Network supplier profile for a supplier. Includes company info, certifications, and capabilities.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_supplier_profile(supplier_id: str) -> str:
        try:
            result = await client.fetch_resource(SUPPLIER_PROFILE_API, f"profiles/{supplier_id}")
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_supplier_get_qualifications",
        description="Get qualification and certification details for a supplier.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_qualifications(supplier_id: str) -> str:
        try:
            result = await client.fetch_resource(SUPPLIER_DATA_API, f"suppliers/{supplier_id}/qualifications")
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)
