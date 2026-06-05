import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

SUPPLIER_INFORMATION_API = "supplier-information/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:
    supplier_client = client.with_api("supplier_information")

    @mcp.tool(
        name="ariba_supplier_information_list",
        description=(
            "Verify buyer-supplier relationships and collaboration types on SAP Business Network. "
            "Returns details about suppliers linked to the buyer, including their ANID and "
            "enabled collaboration features (e.g., Supply Chain, Forecast, Catalog). "
            "Note: This is a buyer-facing API — the buyer ANID is configured in AribaClient settings."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def supplier_information_list(
        anid: str,
        filter: str | None = None,
        top: int | None = None,
        skip: int | None = None,
    ) -> str:
        try:
            params: dict = {"anid": anid}
            if filter:
                params["$filter"] = filter
            if top is not None:
                params["$top"] = top
            if skip is not None:
                params["$skip"] = skip
            result = await supplier_client.fetch_resource(
                SUPPLIER_INFORMATION_API, "suppliers", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)
