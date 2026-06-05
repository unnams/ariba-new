import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

PLANNING_COLLABORATION_SUPPLIER_API = "planning-collaboration-supplier/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_supplier_forecast_list",
        description=(
            "Retrieve forecast records from buyers via the Planning Collaboration Supplier API. "
            "Returns demand forecast information for a supplier's Business Network user ID (ANID). "
            "Supports filtering by buyer, plant, part numbers, and date range."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def supplier_forecast_list(
        anid: str,
        filter: str | None = None,
        orderby: str | None = None,
        top: int | None = None,
        skip: int | None = None,
        count: bool | None = None,
    ) -> str:
        try:
            params: dict = {"anid": anid}
            if filter:
                params["$filter"] = filter
            if orderby:
                params["$orderby"] = orderby
            if top is not None:
                params["$top"] = top
            if skip is not None:
                params["$skip"] = skip
            if count is not None:
                params["$count"] = str(count).lower()
            result = await client.fetch_resource(
                PLANNING_COLLABORATION_SUPPLIER_API, "forecast", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_supplier_inventory_list",
        description=(
            "Retrieve supplier inventory records from the Planning Collaboration Supplier API. "
            "Returns inventory information for a supplier's Business Network user ID (ANID). "
            "Supports filtering by buyer, plant, and part numbers."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def supplier_inventory_list(
        anid: str,
        filter: str | None = None,
        orderby: str | None = None,
        top: int | None = None,
        skip: int | None = None,
        count: bool | None = None,
    ) -> str:
        try:
            params: dict = {"anid": anid}
            if filter:
                params["$filter"] = filter
            if orderby:
                params["$orderby"] = orderby
            if top is not None:
                params["$top"] = top
            if skip is not None:
                params["$skip"] = skip
            if count is not None:
                params["$count"] = str(count).lower()
            result = await client.fetch_resource(
                PLANNING_COLLABORATION_SUPPLIER_API, "supplierInventory", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_supplier_managed_inventory_list",
        description=(
            "Retrieve supplier-managed inventory (SMI) records from the Planning Collaboration Supplier API. "
            "Returns SMI information for a supplier's Business Network user ID (ANID). "
            "Supports filtering by buyer, plant, part numbers, and date range."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def supplier_managed_inventory_list(
        anid: str,
        filter: str | None = None,
        orderby: str | None = None,
        top: int | None = None,
        skip: int | None = None,
        count: bool | None = None,
    ) -> str:
        try:
            params: dict = {"anid": anid}
            if filter:
                params["$filter"] = filter
            if orderby:
                params["$orderby"] = orderby
            if top is not None:
                params["$top"] = top
            if skip is not None:
                params["$skip"] = skip
            if count is not None:
                params["$count"] = str(count).lower()
            result = await client.fetch_resource(
                PLANNING_COLLABORATION_SUPPLIER_API, "supplierManagedInventory", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)
