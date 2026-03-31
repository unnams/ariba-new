import json

from fastmcp import FastMCP
from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

EVENT_STATUS_API = "https://openapi.ariba.com/api/strategicsourcing-eventstatus/v2/prod"


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
            result = await client.fetch(
                f"{EVENT_STATUS_API}/events/{event_id}"
            )

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
            result = await client.fetch(
                f"{EVENT_STATUS_API}/events",
                params={
                    "pageToken": page_token
                }
            )

            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)