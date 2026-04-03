"""Pricing API for Product Sourcing.

Owner: Pranathi
Prod URL: https://openapi.ariba.com/api/pricing/v1/prod

Fetch pricing details for items in Ariba based on supplier, item,
or contract context.

Authentication: OAuth 2.0 Bearer token + apiKey header (Pranathi credentials)
"""

import json
import os

import httpx
from fastmcp import FastMCP

from ariba_mcp.auth import DirectAuthClient
from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

BASE_URL = "https://openapi.ariba.com/api/pricing/v1/prod"


def _make_auth() -> DirectAuthClient:
    return DirectAuthClient(
        client_id=os.getenv("PRANATHI_CLIENT_ID", ""),
        client_secret=os.getenv("PRANATHI_CLIENT_SECRET", ""),
        api_key=os.getenv("PRANATHI_API_KEY", ""),
    )


def register(mcp: FastMCP, client: AribaClient) -> None:

    _auth = _make_auth()

    @mcp.tool(
        name="ariba_get_pricing_details",
        description=(
            "Retrieve pricing details for items in Ariba. "
            "Used to fetch price based on supplier, item, or contract context. "
            "Pass filters as a JSON string, e.g. '{\"itemId\":\"123\",\"supplier\":\"ABC\"}'."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_pricing_details(
        filters: str | None = None,
        page_token: str | None = None,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            params: dict = {"realm": client.realm}
            if filters:
                filter_dict = json.loads(filters)
                params["filters"] = json.dumps(filter_dict)
            if page_token:
                params["pageToken"] = page_token

            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/pricingDetails",
                    headers=headers,
                    params=params,
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)
