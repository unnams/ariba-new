import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

RISK_CATEGORY_API = "https://openapi.ariba.com/api/risk-category-information/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_risk_categories_list",
        description=(
            "Retrieve a list of available risk categories defined in the SAP Ariba realm. "
            "Risk categories are used to classify supplier risk data (e.g., financial, "
            "compliance, sustainability). Use the returned category IDs when pushing "
            "risk data via ariba_risk_category_data_update."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def risk_categories_list(
        realm: str,
        top: int | None = None,
        skip: int | None = None,
    ) -> str:
        try:
            params: dict = {"realm": realm}
            if top is not None:
                params["$top"] = top
            if skip is not None:
                params["$skip"] = skip
            result = await client.fetch_resource(
                RISK_CATEGORY_API, "riskCategories", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_risk_category_data_update",
        description=(
            "Add or update supplier-level risk category data in SAP Ariba Supplier Risk. "
            "Pushes external risk scores or compliance data points into a supplier's "
            "risk profile under a specific risk category. Use ariba_risk_categories_list "
            "to find valid category IDs before calling this tool."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
    )
    async def risk_category_data_update(
        realm: str,
        body: dict,
    ) -> str:
        try:
            result = await client.post_resource(
                RISK_CATEGORY_API,
                "riskCategoryData",
                {"realm": realm},
                body,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)
