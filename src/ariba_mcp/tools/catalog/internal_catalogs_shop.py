import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

API_PATH = "ariba-catalog-provider/v1/prod"
BASE_URL = "https://openapi.ariba.com/api/ariba-catalog-provider/v1/prod"


def _resolve_shop_id(shop_id: str | None) -> str | None:
    return shop_id


MISSING_SHOP_ID_MSG = (
    "Missing required `shop_id`. Set `INTERNAL_CATALOGS_SHOP_ID` in `.env` "
    "or pass `shop_id` directly. SAP Ariba requires calls like "
    "`GET /Shops({shopID})` — calling `/Shops` alone is not supported."
)


def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_catalog_internal_get_shop",
        description=(
            "Retrieve all items and facets from the catalogs in a specific internal shop. "
            "Calls GET /Shops({shopID}). "
            "If `shop_id` is not passed, falls back to `INTERNAL_CATALOGS_SHOP_ID` in `.env`."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def catalog_internal_get_shop(shop_id: str | None = None) -> str:
        try:
            shop_id = _resolve_shop_id(shop_id)
            if not shop_id:
                return MISSING_SHOP_ID_MSG
            url = f"{BASE_URL}/Shops({shop_id})"
            result = await client.get(url, params={"realm": client.realm})
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_catalog_internal_get_items",
        description=(
            "Return all items and their details from the catalogs in a specific internal shop. "
            "Calls GET /Shops({shopID})/Items. "
            "Optionally filter by `search_term` and limit fields with `select_fields`. "
            "If `shop_id` is not passed, falls back to `INTERNAL_CATALOGS_SHOP_ID` in `.env`."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def catalog_internal_get_items(
        shop_id: str | None = None,
        search_term: str | None = None,
        select_fields: str | None = None,
    ) -> str:
        try:
            shop_id = _resolve_shop_id(shop_id)
            if not shop_id:
                return MISSING_SHOP_ID_MSG
            params: dict = {"realm": client.realm}
            if search_term:
                params["$search"] = search_term
            if select_fields:
                params["$select"] = select_fields
            url = f"{BASE_URL}/Shops({shop_id})/Items"
            result = await client.get(url, params=params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_catalog_internal_autocomplete",
        description=(
            "Typeahead search: retrieve matching search suggestions from an internal catalog shop. "
            "Calls GET /Shops({shopID})/AutoComplete. "
            "Requires Search 3.0 to be enabled on your site. "
            "If `shop_id` is not passed, falls back to `INTERNAL_CATALOGS_SHOP_ID` in `.env`."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def catalog_internal_autocomplete(
        search_term: str,
        shop_id: str | None = None,
    ) -> str:
        try:
            shop_id = _resolve_shop_id(shop_id)
            if not shop_id:
                return MISSING_SHOP_ID_MSG
            params: dict = {"realm": client.realm, "$search": search_term}
            url = f"{BASE_URL}/Shops({shop_id})/AutoComplete"
            result = await client.get(url, params=params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)
