import json
import httpx

from fastmcp import FastMCP
from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_general_settings
from ariba_mcp.errors import handle_ariba_error

EVENT_STATUS_API_CANDIDATES = [
    "https://openapi.ariba.com/api/strategicsourcing-eventstatus/v2/prod",
    "https://openapi.ariba.com/api/strategicsourcing-eventstatus/v1/prod",
    "https://openapi.ariba.com/api/strategic-sourcing-eventstatus/v2/prod",
]


async def _fetch_with_endpoint_fallback(active_client: AribaClient, suffix: str, params: dict | None = None) -> dict:
    settin
    gs = get_general_settings()
    if settings.ariba_event_status_api:
        candidates = [settings.ariba_event_status_api.rstrip("/")]
    else:
        candidates = list(EVENT_STATUS_API_CANDIDATES)

    last_error: Exception | None = None
    for base in candidates:
        url = f"{base}{suffix}"
        try:
            return await active_client.fetch(url, params=params)
        except httpx.HTTPStatusError as e:
            last_error = e
            text = (e.response.text or "").lower()
            # Retry only when endpoint is clearly missing; stop on auth/permission errors.
            if e.response.status_code == 404 and ("<html" in text or "no static resource" in text):
                continue
            raise
        except Exception as e:  # pragma: no cover - network dependent
            last_error = e
            continue

    if last_error:
        raise last_error
    raise RuntimeError("No event status endpoint candidates configured")


def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_get_event_status",
        description=(
            "Retrieve the status of a sourcing event in Ariba. "
            "Used to check if an event is open, closed, or awarded."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_event_status(
        event_id: str,
    ) -> str:
        try:
            active_client = AribaClient(get_general_settings())
            result = await _fetch_with_endpoint_fallback(active_client, f"/events/{event_id}")

            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)


    @mcp.tool(
        name="ariba_list_event_status",
        description=(
            "Retrieve list of sourcing events with their statuses."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def list_event_status(
        page_token: str | None = None,
    ) -> str:
        try:
            active_client = AribaClient(get_general_settings())
            result = await _fetch_with_endpoint_fallback(
                active_client,
                "/events",
                params={
                    "pageToken": page_token
                },
            )

            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)
