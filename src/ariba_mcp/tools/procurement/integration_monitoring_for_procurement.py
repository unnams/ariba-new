import json

import httpx
from fastmcp import FastMCP

from ariba_mcp.auth import DirectAuthClient
from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_settings
from ariba_mcp.errors import handle_ariba_error

BASE_URL = "https://openapi.ariba.com/api/procurement-eventstatus/v2/prod"


def _make_auth() -> DirectAuthClient:
    s = get_settings()
    return DirectAuthClient(
        client_id=s.integration_monitoring_client_id,
        client_secret=s.integration_monitoring_client_secret,
        api_key=s.integration_monitoring_api_key,
    )


def register(mcp: FastMCP, client: AribaClient) -> None:

    _auth = _make_auth()

    @mcp.tool(
        name="ariba_procurement_integration_event_status",
        description=(
            "Retrieve the status of a specific integration event (data import or export task) "
            "in SAP Ariba Procurement. Returns the current running status of the event, "
            "or the last run status if the event is not currently running. "
            "Useful for automating and monitoring batch ITK and file-channel integration jobs."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def procurement_integration_event_status(
        realm: str,
        task_name: str,
        filter: str | None = None,
        top: int | None = None,
        skip: int | None = None,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            params: dict = {
                "realm": realm,
                "taskName": task_name,
            }
            if filter:
                params["$filter"] = filter
            if top is not None:
                params["$top"] = top
            if skip is not None:
                params["$skip"] = skip
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/tasks",
                    headers=headers,
                    params=params,
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)
