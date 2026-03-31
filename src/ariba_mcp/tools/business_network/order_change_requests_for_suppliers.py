"""Order Change Requests API for Suppliers.

Owner: Shabreen Taj
Docs: https://help.sap.com/doc/a18df06872cc41dab5617273313a23d4/cloud/en-US/index.html

This API is for SAP Business Network suppliers with SAP Business Network for
Supply Chain enablement who want to extract change request information.

Prerequisites:
  - SAP Ariba Developer Portal access
  - SAP Business Network for Supply Chain enablement
  - OAuth authentication configured
  - API Management enabled in Seller account settings
"""

import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

# TODO: Confirm exact API path slug from the Developer Portal
# "Environment Details" for this API.
ORDER_CHANGE_REQUESTS_SUPPLIER_API = "order-change-requests-supplier/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_supplier_change_requests_list",
        description=(
            "List order change requests received by a supplier from Ariba Network. "
            "Get change request information associated with a supplier's "
            "Business Network user ID (ANID)."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def supplier_change_requests_list(
        anid: str,
        filter: str | None = None,
        page_token: str | None = None,
    ) -> str:
        try:
            params: dict = {"anid": anid}
            if filter:
                params["$filter"] = filter
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(
                ORDER_CHANGE_REQUESTS_SUPPLIER_API, "changeRequests", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_supplier_change_request_responses_list",
        description=(
            "List responses to order change requests sent by a supplier on Ariba Network. "
            "Get change request response information associated with a supplier's "
            "Business Network user ID (ANID)."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def supplier_change_request_responses_list(
        anid: str,
        filter: str | None = None,
        page_token: str | None = None,
    ) -> str:
        try:
            params: dict = {"anid": anid}
            if filter:
                params["$filter"] = filter
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(
                ORDER_CHANGE_REQUESTS_SUPPLIER_API, "changeRequestResponses", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_supplier_change_request_confirmations_list",
        description=(
            "List order change request confirmations sent to a supplier on Ariba Network. "
            "Get confirmation information for change requests associated with a "
            "supplier's Business Network user ID (ANID)."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def supplier_change_request_confirmations_list(
        anid: str,
        filter: str | None = None,
        page_token: str | None = None,
    ) -> str:
        try:
            params: dict = {"anid": anid}
            if filter:
                params["$filter"] = filter
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(
                ORDER_CHANGE_REQUESTS_SUPPLIER_API, "changeRequestConfirmations", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)