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
            "List items added to a sourcing event. "
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
        name="ariba_event_add_line_item_with_price_quantity",
        description=(
            "Add a new sourcing event line item with Price and Quantity terms. "
            "Ask only for event_id, item title, quantity, price, currency, and unit of measure. "
            "Do not ask for fieldId."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def add_line_item_with_price_quantity(
        event_id: str,
        title: str,
        quantity: float,
        price: float,
        currency: str = "USD",
        unit_of_measure_code: str = "EA",
        reserve_price: float | None = None,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            reserve_price = reserve_price if reserve_price is not None else price
            payload = [
                {
                    "title": title,
                    "itemType": 4,
                    "terms": [
                        {
                            "title": "Price",
                            "historicValueProperty": 1,
                            "reserverValueProperty": 1,
                            "value": {
                                "moneyValue": {
                                    "amount": price,
                                    "currency": currency,
                                }
                            },
                            "historyValue": {
                                "moneyValue": {
                                    "amount": price,
                                    "currency": currency,
                                }
                            },
                            "reserveValue": {
                                "moneyValue": {
                                    "amount": reserve_price,
                                    "currency": currency,
                                }
                            },
                        },
                        {
                            "title": "Quantity",
                            "value": {
                                "quantityValue": {
                                    "amount": quantity,
                                    "unitOfMeasureCode": unit_of_measure_code,
                                }
                            },
                        },
                    ],
                }
            ]

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
        name="ariba_event_create",
        description=(
            "Create a new sourcing event. "
            "Required: title and template_id.""event_type_name defaults to RFQ. "
             "Do not ask for owner_email or parent_project_id."
            
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

           if not template_id:
            return json.dumps({
                "error": "Missing required field.",
                "missing": ["template_id"],
                "hint": "Set SOURCING_DEFAULT_TEMPLATE_ID env var or pass template_id explicitly.",
            })

        params = _user_params(client.realm, user, password_adapter)
        params["inheritTerms"] = "true"
        params["removeEmptyOwnerTerms"] = "true"

        payload = {
            "title": title,
            "templateDocumentInternalId": template_id,
            "eventTypeName": event_type_name,
            "isTest": is_test,
        }

        if description:
            payload["description"] = description

        if extra_fields:
            payload.update(json.loads(extra_fields))

        headers = await _auth.get_headers()
        headers["Content-Type"] = "application/json"

        async with httpx.AsyncClient() as http:
            resp = await http.post(
                f"{BASE_URL}/events",
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

    @mcp.tool(
        name="ariba_event_get_supplier_invitation",
        description="Get a specific supplier's invitation/bid for an event.",
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
                    headers=headers,
                    params=params,
                    timeout=60,
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
                    headers=headers,
                    params=params,
                    timeout=60,
                )
                resp.raise_for_status()

            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_publish",
        description="Publish a sourcing event so suppliers can see and respond to it.",
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
                    headers=headers,
                    params=params,
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()

            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)
