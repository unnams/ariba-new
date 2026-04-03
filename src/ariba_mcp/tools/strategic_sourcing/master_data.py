"""Master Data Retrieval API for Strategic Sourcing.

Owner: Pranathi
Prod URL: https://openapi.ariba.com/api/sourcing-mds-search/v1/prod

Fetch master data entities (commodities, regions, departments, company codes)
using a search term.

Authentication: OAuth 2.0 Bearer token + apiKey header (Pranathi credentials)
"""

import json
import os

import httpx
from fastmcp import FastMCP

from ariba_mcp.auth import DirectAuthClient
from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

BASE_URL = "https://openapi.ariba.com/api/sourcing-mds-search/v1/prod"


def _make_auth() -> DirectAuthClient:
    return DirectAuthClient(
        client_id=os.getenv("PRANATHI_CLIENT_ID", ""),
        client_secret=os.getenv("PRANATHI_CLIENT_SECRET", ""),
        api_key=os.getenv("PRANATHI_API_KEY", ""),
    )


def register(mcp: FastMCP, client: AribaClient) -> None:

    _auth = _make_auth()

    @mcp.tool(
        name="ariba_master_data_retrieval",
        description=(
            "Retrieve master data from Ariba Strategic Sourcing. "
            "Fetch commodities, regions, departments, company codes using a search term."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def master_data_retrieval(
        search_term: str,
        page_token: str | None = None,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            params: dict = {
                "realm": client.realm,
                "filters": json.dumps({"searchTerm": search_term}),
            }
            if page_token:
                params["pageToken"] = page_token

            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/masterData",
                    headers=headers,
                    params=params,
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)
