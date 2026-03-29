"""Supplier Risk APIs for SAP Ariba.

Covers:
- Risk Exposure API:                          risk-exposure/v1/prod
- Supplier Risk Engagements API:              risk-engagements/v1/prod
- Risk Category Information API:              risk-category/v1/prod

Docs: https://help.sap.com/docs/ariba-apis
"""

import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

RISK_EXPOSURE_API = "risk-exposure/v1/prod"
RISK_ENGAGEMENTS_API = "risk-engagements/v1/prod"
RISK_CATEGORY_API = "risk-category/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register Supplier Risk tools."""

    @mcp.tool(
        name="ariba_risk_get_exposure",
        description="Get risk exposure data for a specific supplier. Shows overall risk score and category breakdown.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_exposure(supplier_id: str) -> str:
        try:
            result = await client.fetch_resource(RISK_EXPOSURE_API, f"suppliers/{supplier_id}/exposure")
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_risk_list_exposures",
        description="List risk exposures across all suppliers. Returns suppliers with their risk scores.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_exposures(page_token: str | None = None) -> str:
        try:
            params = {}
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(RISK_EXPOSURE_API, "exposures", params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_risk_list_engagements",
        description="List supplier risk engagement workflows. Shows active risk assessments and mitigation activities.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_engagements(page_token: str | None = None) -> str:
        try:
            params = {}
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(RISK_ENGAGEMENTS_API, "engagements", params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_risk_get_categories",
        description="Get the risk category taxonomy. Returns all risk categories used for supplier risk scoring.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_categories() -> str:
        try:
            result = await client.fetch_resource(RISK_CATEGORY_API, "categories")
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)
