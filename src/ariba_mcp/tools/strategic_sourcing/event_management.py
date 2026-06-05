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
            "items_data is a JSON string representing the items array per Ariba schema. "
            "itemType values: 2=Section, 3=Question, 4=LineItem, 5=Lot. "
            "To create a questionnaire that can accept a file upload, add a Section, then a "
            "Question whose terms include an Attachment-typed term. Example payload:\n"
            '{"items": ['
            '{"itemType": 2, "title": "Technical Requirements", "parentItem": "ROOT"}, '
            '{"itemType": 3, "title": "Please review the attached spec and confirm compliance", '
            '"parentItem": "<sectionItemId from the section response>", '
            '"terms": [{"fieldId": "RITAATTACHIFZ000001", "dataType": "Attachment"}]}'
            "]}\n"
            "After the question is created, upload the file with ariba_event_item_add_attachment "
            "using the question's itemId and the term's fieldId."
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
        name="ariba_event_item_add_attachment",
        description=(
            "Upload a file as an attachment to a specific item (Question/LineItem) in a "
            "Draft sourcing event. Use this after ariba_event_add_items has created an item "
            "with an Attachment-typed term.\n"
            "- file_content: the document body. For text/markdown, pass the raw string. "
            "For binary files (PDF, DOCX), pass base64 and set is_base64=True.\n"
            "- field_id: the term ID for the attachment slot, e.g. 'RITAATTACHIFZ000001' "
            "(visible on the item's terms in ariba_event_list_items).\n"
            "- file_name: filename Ariba will display, e.g. 'requirements.md'.\n"
            "- content_type: MIME type, default text/plain. Use application/pdf, "
            "text/markdown, etc. as appropriate.\n"
            "Note: the event must be in Draft status; uploads to published events are rejected."
        ),
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
                    headers=headers, params=params,
                    files={"file": (file_name, raw, content_type)},
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_create",
        description=(
            "Create a new sourcing event (RFx/RFP/Auction) in Ariba. "
            "Required: title. "
            "owner_email, template_id, and parent_project_id are OPTIONAL — when omitted "
            "they default to the server-configured SOURCING_OWNER_EMAIL / "
            "SOURCING_DEFAULT_TEMPLATE_ID / SOURCING_DEFAULT_WORKSPACE_ID values for this "
            "realm. Do NOT ask the user for these; just call the tool with only the title "
            "(plus description/owner_name/is_test/extra_fields if relevant)."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def create_event(
        title: str,  
        
        owner_email: str | None = None,
        template_id: str | None = None,
        parent_project_id: str | None = None,
        description: str = "",
        owner_name: str | None = None,
        is_test: bool = True,
        extra_fields: str | None = None,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            s = get_settings()
            owner_email = owner_email or s.sourcing_owner_email
            template_id = template_id or s.sourcing_default_template_id
            parent_project_id = parent_project_id or s.sourcing_default_workspace_id
            missing = [
                name for name, val in (
                    ("owner_email", owner_email),
                    ("template_id", template_id),
                    ("parent_project_id", parent_project_id),
                ) if not val
            ]
            if missing:
                return json.dumps({
                    "error": "Missing required field(s) and no server defaults configured.",
                    "missing": missing,
                    "hint": (
                        "Set SOURCING_OWNER_EMAIL / SOURCING_DEFAULT_TEMPLATE_ID / "
                        "SOURCING_DEFAULT_WORKSPACE_ID env vars on the MCP server, "
                        "or pass them explicitly."
                    ),
                })
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
