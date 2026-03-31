"""Risk Category Information API.

Owner: Shabreen
Docs: https://help.sap.com/doc/3a9efde5fd074398b9ae284a478f98e4/cloud/en-US/index.html

This API allows developers to build applications that add and manage 
supplier-level data within SAP Ariba risk profiles.

Endpoints implemented:
  GET  /riskCategories – retrieve list of defined risk categories
  POST /riskData       – add or update risk data for specific suppliers
"""

import json
from fastmcp import FastMCP
from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

RISK_CATEGORY_API = "risk-category-information/v1/prod"

def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_risk_categories_list",
        description="Retrieve a list of available risk categories defined in the realm.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True},
    )
    async def risk_categories_list(realm: str) -> str:
        """
        Args:
            realm: Required. The target SAP Ariba realm.
        """
        try:
            params = {"realm": realm}
            result = await client.fetch_resource(
                RISK_CATEGORY_API, "riskCategories", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_risk_data_update",
        description=(
            "Add or update supplier-level risk data. This tool pushes external "
            "risk scores or data points into a supplier's risk profile."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": False},
    )
    async def risk_data_update(realm: str, body: dict) -> str:
        """
        Args:
            realm: Required. The target SAP Ariba realm.
            body:  Required. JSON payload containing the risk data (supplierId, 
                   category, score/value, etc.).
        """
        try:
            # Assumes client.post_resource is implemented to handle POST requests
            result = await client.post_resource(
                RISK_CATEGORY_API, "riskData", {"realm": realm}, body
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)