import json

import httpx
from fastmcp import FastMCP

from ariba_mcp.auth import DirectAuthClient
from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_settings
from ariba_mcp.errors import handle_ariba_error

BASE_URL = "https://openapi.ariba.com/api/pricing/v1/prod"


def _make_auth() -> DirectAuthClient:
    s = get_settings()
    return DirectAuthClient(
        client_id=s.pricing_client_id,
        client_secret=s.pricing_client_secret,
        api_key=s.pricing_api_key,
    )


def register(mcp: FastMCP, client: AribaClient) -> None:

    _auth = _make_auth()

    @mcp.tool(
        name="ariba_get_pricing_changes",
        description=(
            "Get pricing data changes for a one-day/time window from Ariba Product Sourcing. "
            "from_date and to_date format: ISO 8601 with offset, e.g. '2024-01-01T00:00:00+05:30'. "
            "If unspecified, defaults to a 24h window ending now (UTC)."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_pricing_changes(
        from_date: str,
        to_date: str,
        top: int = 50,
        skip: int = 0,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            params = {
                "realm": client.realm,
                "$filter": f"fromdate eq '{from_date}' and todate eq '{to_date}'",
                "$top": top,
                "$skip": skip,
            }
            async with httpx.AsyncClient() as http:
                resp = await http.get(f"{BASE_URL}/objects", headers=headers, params=params, timeout=60)
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)
