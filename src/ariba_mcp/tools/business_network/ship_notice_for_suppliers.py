import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

SHIP_NOTICE_SUPPLIER_API = "ship-notice-supplier/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_supplier_ship_notices_list",
        description=(
            "List ship notices for a supplier from Ariba Network. "
            "Retrieves ship notice header information associated with a supplier's "
            "Business Network user ID (ANID). Supports date-range filtering and pagination."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def supplier_ship_notices_list(
        anid: str,
        filter: str | None = None,
        top: int | None = None,
        page_token: str | None = None,
    ) -> str:
        try:
            params: dict = {"anid": anid}
            if filter:
                params["$filter"] = filter
            if top:
                params["$top"] = top
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(
                SHIP_NOTICE_SUPPLIER_API, "shipNotices", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_supplier_ship_notice_items_list",
        description=(
            "List line items for a specific ship notice from Ariba Network. "
            "Retrieves item-level details for a ship notice associated with a "
            "supplier's Business Network user ID (ANID)."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def supplier_ship_notice_items_list(
        anid: str,
        filter: str | None = None,
        top: int | None = None,
        page_token: str | None = None,
    ) -> str:
        try:
            params: dict = {"anid": anid}
            if filter:
                params["$filter"] = filter
            if top:
                params["$top"] = top
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(
                SHIP_NOTICE_SUPPLIER_API, "items", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)
