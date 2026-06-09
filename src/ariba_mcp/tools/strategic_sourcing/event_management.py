import base64
import json

import httpx
from fastmcp import FastMCP

from ariba_mcp.auth import DirectAuthClient
from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_settings
from ariba_mcp.errors import handle_ariba_error

BASE_URL = "https://openapi.ariba.com/api/sourcing-event/v2/prod"


def _make_auth() -> DirectAuthClient:
    s = get_settings()
    return DirectAuthClient(
        client_id=s.event_mgmt_client_id,
        client_secret=s.event_mgmt_client_secret,
        api_key=s.event_mgmt_api_key,
    )


def _user_params(realm: str, user: str | None, password_adapter: str | None) -> dict:
    s = get_settings()
    return {
        "realm": realm,
        "user": user or s.sourcing_pm_user,
        "passwordAdapter": password_adapter or s.sourcing_pm_password_adapter,
    }


def register(mcp: FastMCP, client: AribaClient) -> None:
    _auth = _make_auth()

    @mcp.tool(
        name="ariba_event_list_items",
        description="List items added to a sourcing event.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_event_items(
        event_id: str,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            params = _user_params(client.realm, user, password_adapter)
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/events/{event_id}/items",
                    headers=headers,
                    params=params,
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_add_items",
        description="Add items to an existing sourcing event. items_data must be a JSON string per Ariba schema.",
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def add_event_items(
        event_id: str,
        items_data: str,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            payload = json.loads(items_data)
            headers = await _auth.get_headers()
            headers["Content-Type"] = "application/json"
            params = _user_params(client.realm, user, password_adapter)
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    f"{BASE_URL}/events/{event_id}/items",
                    headers=headers,
                    params=params,
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_item_add_attachment",
        description="Upload a file as an attachment to a specific item in a Draft sourcing event.",
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def add_event_item_attachment(
        event_id: str,
        item_id: str,
        field_id: str,
        file_content: str,
        file_name: str,
        content_type: str = "text/plain",
        is_base64: bool = False,
        is_reference: bool = False,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            raw = base64.b64decode(file_content) if is_base64 else file_content.encode("utf-8")
            params = _user_params(client.realm, user, password_adapter)
            params["fieldId"] = field_id
            params["isReference"] = "true" if is_reference else "false"
            headers = await _auth.get_headers()
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    f"{BASE_URL}/events/{event_id}/items/{item_id}/attachments",
                    headers=headers,
                    params=params,
                    files={"file": (file_name, raw, content_type)},
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_update_item",
        description="Update an existing sourcing event item or item terms such as Quantity.",
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def update_event_item(
        event_id: str,
        item_id: str,
        item_data: str,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            payload = json.loads(item_data)
            headers = await _auth.get_headers()
            headers["Content-Type"] = "application/json"
            params = _user_params(client.realm, user, password_adapter)
            async with httpx.AsyncClient() as http:
                resp = await http.patch(
                    f"{BASE_URL}/events/{event_id}/items/{item_id}",
                    headers=headers,
                    params=params,
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_add_supplier_invitations",
        description=(
            "Invite a supplier to a sourcing event using supplier email only. "
            "Do not ask for ANID or supplier organization ID."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def add_supplier_invitations(
        event_id: str,
        supplier_email: str,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            adapter = password_adapter or get_settings().sourcing_pm_password_adapter
            payload = [
                {
                    "contacts": [
                        {
                            "uniqueName": supplier_email,
                            "passwordAdapter": adapter,
                        }
                    ]
                }
            ]
            headers = await _auth.get_headers()
            headers["Content-Type"] = "application/json"
            params = _user_params(client.realm, user, password_adapter)
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    f"{BASE_URL}/events/{event_id}/supplierInvitations",
                    headers=headers,
                    params=params,
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    # Keep your create_event, get_supplier_invitation, get_supplier_bids,
    # publish_event, and validate_event_publish below this point at same 4-space indentation.
