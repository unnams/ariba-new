import json

from fastmcp import FastMCP
from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_profile_settings
from ariba_mcp.errors import handle_ariba_error

SOURCING_APPROVAL_API = "https://openapi.ariba.com/api/sourcing-approval/v2/prod"



def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_get_sourcing_approvals",
        description=(
            "Retrieve pending sourcing approval tasks from Ariba. "
            "Used to fetch approvals for sourcing projects, contracts, or supplier management."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_sourcing_approvals(
        user: str | None = None,
        password_adapter: str | None = None,
        document_type: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> str:
        try:
            active_client = AribaClient(get_profile_settings("EXTERNAL_APPROVAL"))
            effective_user = user or active_client._settings.ariba_user
            effective_adapter = password_adapter or active_client._settings.ariba_password_adapter
            result = await active_client.fetch(
                f"{SOURCING_APPROVAL_API}/pendingApprovables",
                params={
                    "user": effective_user,
                    "passwordAdapter": effective_adapter,
                    "documentType": document_type,
                    "offset": offset,
                    "limit": limit,
                }
            )

            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_get_sourcing_approval_changes",
        description=(
            "Retrieve changed approval entities from External Approval API. "
            "Useful for incremental sync using lastChangeId."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_sourcing_approval_changes(
        last_change_id: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        need_total: bool | None = None,
        filter_expr: str | None = None,
    ) -> str:
        try:
            active_client = AribaClient(get_profile_settings("EXTERNAL_APPROVAL"))
            result = await active_client.fetch(
                f"{SOURCING_APPROVAL_API}/changes",
                params={
                    "lastChangeId": last_change_id,
                    "offset": offset,
                    "limit": limit,
                    "needTotal": need_total,
                    "$filter": filter_expr,
                },
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)


    @mcp.tool(
        name="ariba_approve_sourcing_task",
        description=(
            "Approve a sourcing task in Ariba. "
            "Provide approval ID and optional comments."
        ),
        annotations={
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def approve_sourcing_task(
        approval_id: str,
        comments: str | None = None,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            active_client = AribaClient(get_profile_settings("EXTERNAL_APPROVAL"))
            effective_user = user or active_client._settings.ariba_user
            effective_adapter = password_adapter or active_client._settings.ariba_password_adapter
            if not effective_user or not effective_adapter:
                return json.dumps(
                    {
                        "error": True,
                        "message": (
                            "Approve action requires `user` and `password_adapter`, "
                            "or set ARIBA_EXTERNAL_APPROVAL_USER/USERID and "
                            "ARIBA_EXTERNAL_APPROVAL_PASSWORD_ADAPTER in .env."
                        ),
                    }
                )

            payload = {
                "actionableType": "Task",
                "uniqueName": approval_id,
                "actionName": "Approve",
                "options": {"comment": comments or "Approved via MCP"},
            }

            result = await active_client.post(
                f"{SOURCING_APPROVAL_API}/action",
                json=payload,
                params={
                    "user": effective_user,
                    "passwordadapter": effective_adapter,
                },
            )

            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)


    @mcp.tool(
        name="ariba_reject_sourcing_task",
        description=(
            "Reject a sourcing task in Ariba with comments."
        ),
        annotations={
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def reject_sourcing_task(
        approval_id: str,
        comments: str,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            active_client = AribaClient(get_profile_settings("EXTERNAL_APPROVAL"))
            effective_user = user or active_client._settings.ariba_user
            effective_adapter = password_adapter or active_client._settings.ariba_password_adapter
            if not effective_user or not effective_adapter:
                return json.dumps(
                    {
                        "error": True,
                        "message": (
                            "Reject action requires `user` and `password_adapter`, "
                            "or set ARIBA_EXTERNAL_APPROVAL_USER/USERID and "
                            "ARIBA_EXTERNAL_APPROVAL_PASSWORD_ADAPTER in .env."
                        ),
                    }
                )
            payload = {
                "actionableType": "Task",
                "uniqueName": approval_id,
                "actionName": "Deny",
                "options": {"comment": comments},
            }

            result = await active_client.post(
                f"{SOURCING_APPROVAL_API}/action",
                json=payload,
                params={
                    "user": effective_user,
                    "passwordadapter": effective_adapter,
                },
            )

            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)
