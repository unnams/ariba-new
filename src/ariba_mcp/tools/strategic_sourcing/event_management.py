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
        description=(
            "List items added to a sourcing event (e.g. RFx, Auction). "
            "event_id is the document ID like 'Doc5653890759'."
        ),
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
                    headers=headers, params=params, timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_add_items",
        description=(
            "Add items to an existing sourcing event. "
            "items_data is a JSON string representing the items array per Ariba schema."
        ),
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
                    headers=headers, params=params, json=payload, timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_create",
        description=(
            "Create a new sourcing event (RFx/RFP/Auction) in Ariba. "
            "Required: title, owner_email, template_id (the source RFx template, e.g. 'Doc5613355011'), "
            "parent_project_id (the parent project workspace, e.g. 'WS5653890756'). "
            "Optional: description, owner_name, is_test (defaults true), and extra_fields "
            "(JSON string of additional schema fields to merge into the payload)."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def create_event(
        title: str,
        owner_email: str,
        template_id: str,
        parent_project_id: str,
        description: str = "",
        owner_name: str | None = None,
        is_test: bool = True,
        extra_fields: str | None = None,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            params = _user_params(client.realm, user, password_adapter)
            payload = {
                "title": title,
                "description": description,
                "owner": {
                    "uniqueName": owner_email,
                    "passwordAdapter": params["passwordAdapter"],
                    "name": owner_name or owner_email,
                },
                "templateDocumentInternalId": template_id,
                "parentProjectId": parent_project_id,
                "isTest": is_test,
            }
            if extra_fields:
                payload.update(json.loads(extra_fields))
            headers = await _auth.get_headers()
            headers["Content-Type"] = "application/json"
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    f"{BASE_URL}/events",
                    headers=headers, params=params, json=payload, timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_add_supplier_invitations",
        description=(
            "Invite suppliers to a sourcing event. "
            "invitations_data is a JSON string of the supplier invitations array."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def add_supplier_invitations(
        event_id: str,
        invitations_data: str,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            payload = json.loads(invitations_data)
            headers = await _auth.get_headers()
            headers["Content-Type"] = "application/json"
            params = _user_params(client.realm, user, password_adapter)
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    f"{BASE_URL}/events/{event_id}/supplierInvitations",
                    headers=headers, params=params, json=payload, timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_get_supplier_invitation",
        description=(
            "Get a specific supplier's invitation/bid for an event. "
            "supplier_user is the supplier's unique user identifier (typically email)."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_supplier_invitation(
        event_id: str,
        supplier_user: str,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            params = _user_params(client.realm, user, password_adapter)
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/events/{event_id}/supplierInvitations/{supplier_user}",
                    headers=headers, params=params, timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_get_supplier_bids",
        description="Fetch all supplier bids submitted for a sourcing event.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_supplier_bids(
        event_id: str,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            params = _user_params(client.realm, user, password_adapter)
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/events/{event_id}/supplierBids",
                    headers=headers, params=params, timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_publish",
        description=(
            "Publish a sourcing event so suppliers can see and respond to it. "
            "Submits a job with PUBLISH action. event_id is the event document ID."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def publish_event(
        event_id: str,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            headers["Content-Type"] = "application/json"
            params = _user_params(client.realm, user, password_adapter)
            payload = {
                "resourceType": "EVENT",
                "actionName": "PUBLISH",
                "ids": {"eventId": event_id},
            }
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    f"{BASE_URL}/jobs",
                    headers=headers, params=params, json=payload, timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)
