import json

import httpx
from fastmcp import FastMCP

from ariba_mcp.auth import DirectAuthClient
from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_settings
from ariba_mcp.errors import handle_ariba_error


def _make_auth() -> DirectAuthClient:
    s = get_settings()
    return DirectAuthClient(
        client_id=s.pranathi_client_id,
        client_secret=s.pranathi_client_secret,
        api_key=s.pranathi_api_key,
    )


def register(mcp: FastMCP, client: AribaClient) -> None:

    _auth = _make_auth()
    BASE_URL = get_settings().ariba_event_status_api

    @mcp.tool(
        name="ariba_get_event_status",
        description=(
            "Retrieve the status of a specific sourcing event by event ID. "
            "Returns whether the event is open, closed, awarded, or in another state."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_event_status(event_id: str) -> str:
        try:
            headers = await _auth.get_headers()
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/events/{event_id}",
                    headers=headers,
                    params={"realm": client.realm},
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_list_event_status",
        description=(
            "List sourcing events with their statuses. "
            "Supports pagination via page_token (returned in previous response)."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_event_status(page_token: str | None = None) -> str:
        try:
            headers = await _auth.get_headers()
            params: dict = {"realm": client.realm}
            if page_token:
                params["pageToken"] = page_token
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/events",
                    headers=headers,
                    params=params,
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)
