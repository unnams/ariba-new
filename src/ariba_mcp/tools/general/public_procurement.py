"""
SAP Ariba Public Procurement Notices Export API tools.

Summary: Export details of notices associated with public procurement events
from SAP Ariba. This API is event-based: first list the notices for an event,
then fetch a specific notice by event ID and notice ID.

This is a synchronous REST API - responses are returned immediately (no job
polling required).

Reference: SAP Ariba Public Procurement Notices Export API
Production base: https://openapi.ariba.com/api/sourcing-event-public-notice/v2/prod
SAP Help: https://help.sap.com/doc/6e4ec89a703a45979aff646dfc6691b0/cloud/en-US/PublicProcurementNoticesExportAPI.pdf
"""

import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

PUBLIC_NOTICE_API = "sourcing-event-public-notice/v2/prod"
PUBLIC_NOTICE_API_NAME = "public_procurement_notices_export"


def _auth_params(realm: str, user: str, password_adapter: str) -> dict[str, str]:
    """Build the query parameters required by the API for buyer authentication."""
    return {
        "realm": realm,
        "user": user,
        "passwordAdapter": password_adapter,
    }


def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_public_notice_list",
        description=(
            "List public procurement notices associated with a specific SAP Ariba sourcing event. "
            "Use the event ID to retrieve all notices published for that event across supported portals."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def public_notice_list(
        realm: str,
        event_id: str,
        user: str,
        password_adapter: str,
    ) -> str:
        """
        Args:
            realm:            Your SAP Ariba site name (for example 'MyCompany-T').
            event_id:         ID of the public procurement sourcing event (for example 'Doc5339181').
            user:             User name of a project owner or team member authorised to view the event.
            password_adapter: Password adapter for the user (for example 'PasswordAdapter1').
        """
        try:
            result = await client.fetch_resource(
                PUBLIC_NOTICE_API,
                f"events/{event_id}/notices",
                _auth_params(realm, user, password_adapter),
                api_name=PUBLIC_NOTICE_API_NAME,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_public_notice_get",
        description=(
            "Retrieve the full details of a single public procurement notice from SAP Ariba. "
            "Requires both the event ID and the notice ID returned by ariba_public_notice_list."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def public_notice_get(
        realm: str,
        event_id: str,
        notice_id: str,
        user: str,
        password_adapter: str,
    ) -> str:
        """
        Args:
            realm:            Your SAP Ariba site name (for example 'MyCompany-T').
            event_id:         ID of the public procurement sourcing event that owns the notice.
            notice_id:        Unique ID of the public procurement notice to retrieve.
            user:             User name of a project owner or team member authorised to view the event.
            password_adapter: Password adapter for the user.
        """
        try:
            result = await client.fetch_resource(
                PUBLIC_NOTICE_API,
                f"events/{event_id}/notices/{notice_id}",
                _auth_params(realm, user, password_adapter),
                api_name=PUBLIC_NOTICE_API_NAME,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_public_notice_list_by_event",
        description=(
            "List all public procurement notices associated with a specific SAP Ariba sourcing event. "
            "Alias of ariba_public_notice_list."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def public_notice_list_by_event(
        realm: str,
        event_id: str,
        user: str,
        password_adapter: str,
    ) -> str:
        """
        Args:
            realm:            Your SAP Ariba site name (for example 'MyCompany-T').
            event_id:         ID of the sourcing event whose notices should be retrieved.
            user:             User name of a project owner or team member authorised to view the event.
            password_adapter: Password adapter for the user.
        """
        try:
            return await public_notice_list(realm, event_id, user, password_adapter)
        except Exception as e:
            return handle_ariba_error(e)
