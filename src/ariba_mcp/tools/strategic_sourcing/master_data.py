import json

import httpx
from fastmcp import FastMCP

from ariba_mcp.auth import DirectAuthClient
from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_settings
from ariba_mcp.errors import handle_ariba_error

BASE_URL = "https://openapi.ariba.com/api/sourcing-mds-search/v1/prod"


def _make_auth() -> DirectAuthClient:
    s = get_settings()
    return DirectAuthClient(
        client_id=s.mds_client_id,
        client_secret=s.mds_client_secret,
        api_key=s.mds_api_key,
    )


def _entity_endpoint(name: str, description: str):
    return name, description


ENTITIES = [
    ("users", "Fetch user master data records from Ariba Sourcing."),
    ("groups", "Fetch group master data records from Ariba Sourcing."),
    ("organizations", "Fetch organization master data, if this entity is enabled in your tenant."),
    ("commoditycodes", "Fetch commodity/category codes used to classify sourcing items."),
    ("countries", "Fetch country master data."),
    ("uoms", "Fetch units of measure (e.g. EA, KG, L)."),
    ("s4regions", "Fetch region master data."),
    ("s4departments", "Fetch department master data."),
    ("preferredsupplierlevels", "Fetch preferred supplier level definitions used in sourcing."),
]


def register(mcp: FastMCP, client: AribaClient) -> None:

    _auth = _make_auth()

    async def _headers() -> dict:
        h = await _auth.get_headers()
        h["X-Realm"] = client.realm
        h["Accept-Language"] = "en"
        return h

    @mcp.tool(
        name="ariba_mds_list_entity_types",
        description=(
            "List all master data entity types supported by the Master Data Retrieval API "
            "available on this site (e.g. users, groups, organizations, commoditycodes, "
            "countries, uoms, regions, departments)."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_entity_types() -> str:
        try:
            headers = await _headers()
            async with httpx.AsyncClient() as http:
                resp = await http.get(f"{BASE_URL}/entityTypes", headers=headers, timeout=60)
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_mds_get_entity_metadata",
        description=(
            "Get the fields and metadata of a specific master data entity, including custom/flex fields. "
            "entity_type examples: users, groups, organizations, commoditycodes, countries, uoms, "
            "s4regions, s4departments, preferredsupplierlevels."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_entity_metadata(entity_type: str) -> str:
        try:
            headers = await _headers()
            async with httpx.AsyncClient() as http:
                resp = await http.get(f"{BASE_URL}/entityTypes/{entity_type}", headers=headers, timeout=60)
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_mds_list_entities",
        description=(
            "List records of a specific master data entity. "
            "entity_type examples: users, groups, organizations, commoditycodes, countries, uoms, "
            "s4regions, s4departments, preferredsupplierlevels. "
            "Supports OData $top, $skip, $orderby, $filter."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_entities(
        entity_type: str,
        top: int = 10,
        skip: int = 0,
        order_by: str | None = None,
        filter_expr: str | None = None,
    ) -> str:
        try:
            headers = await _headers()
            params: dict = {"$top": top, "$skip": skip}
            if order_by:
                params["$orderby"] = order_by
            if filter_expr:
                params["$filter"] = filter_expr
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/entities/{entity_type}",
                    headers=headers, params=params, timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    for entity, desc in ENTITIES:
        def _make_handler(e: str):
            async def handler(top: int = 10, skip: int = 0) -> str:
                try:
                    headers = await _headers()
                    async with httpx.AsyncClient() as http:
                        resp = await http.get(
                            f"{BASE_URL}/entities/{e}",
                            headers=headers, params={"$top": top, "$skip": skip}, timeout=60,
                        )
                        resp.raise_for_status()
                    return json.dumps(resp.json(), default=str)
                except Exception as exc:
                    return handle_ariba_error(exc)
            return handler

        mcp.tool(
            name=f"ariba_mds_list_{entity}",
            description=desc + " Supports pagination via top and skip.",
            annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
        )(_make_handler(entity))
