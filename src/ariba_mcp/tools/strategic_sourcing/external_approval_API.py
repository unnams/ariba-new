import json

import httpx
from fastmcp import FastMCP

from ariba_mcp.auth import DirectAuthClient
from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_settings
from ariba_mcp.errors import handle_ariba_error

BASE_URL = "https://openapi.ariba.com/api/sourcing-approval/v2/prod"


def _make_auth() -> DirectAuthClient:
    s = get_settings()
    return DirectAuthClient(
        client_id=s.sourcing_approval_client_id,
        client_secret=s.sourcing_approval_client_secret,
        api_key=s.sourcing_approval_api_key,
    )


def register(mcp: FastMCP, client: AribaClient) -> None:

    _auth = _make_auth()

    @mcp.tool(
        name="ariba_approval_list_approvables",
        description=(
            "Retrieve pending sourcing approval tasks from Ariba for a specific approver user. "
            "The user must be the actual approver whose pending tasks should be fetched. "
            "Use password_adapter, usually PasswordAdapter1. "
            "document_type is optional and can be blank. "
            "Defaults: limit=10, offset=0."
    ),
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
    async def get_sourcing_approvals(
        user: str,
        password_adapter: str = "PasswordAdapter1",
        document_type: str = "",
        limit: int = 10,
        offset: int = 0,
) -> str:
    try:
        headers = await _auth.get_headers()

        params = {
            "user": user,
            "passwordAdapter": password_adapter,
            "documentType": document_type,
            "limit": limit,
            "offset": offset,
            "realm": client.realm,
        }

        async with httpx.AsyncClient() as http:
            resp = await http.get(
                f"{BASE_URL}/pendingApprovables",
                headers=headers,
                params=params,
                timeout=60,
            )

            if resp.status_code >= 400:
                return json.dumps({
                    "status_code": resp.status_code,
                    "url": str(resp.url),
                    "response": resp.text,
                    "hint": (
                        "Check that the user is the actual approver, the passwordAdapter "
                        "matches that user, and the sourcing approval API credentials have "
                        "read access to pendingApprovables."
                    ),
                })

            return json.dumps(resp.json(), default=str)

    except Exception as e:
        return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_get_sourcing_approval_changes",
        description=(
            "Retrieve changed approval entities for incremental sync. "
            "Pass last_change_id from a previous response to get only new changes. "
            "Supports pagination via offset and limit."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_sourcing_approval_changes(
        last_change_id: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        filter_expr: str | None = None,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            params: dict = {"realm": client.realm}
            if last_change_id is not None:
                params["lastChangeId"] = last_change_id
            if offset is not None:
                params["offset"] = offset
            if limit is not None:
                params["limit"] = limit
            if filter_expr:
                params["$filter"] = filter_expr
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/changes",
                    headers=headers,
                    params=params,
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_approve_sourcing_task",
        description=(
            "Approve a sourcing task in Ariba. "
            "Requires user and password_adapter for user-context auth. "
            "Pass the approval_id (uniqueName of the task) and optional comments."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def approve_sourcing_task(
        approval_id: str,
        user: str,
        password_adapter: str,
        comments: str | None = None,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            headers["Content-Type"] = "application/json"
            payload = {
                "actionableType": "Task",
                "uniqueName": approval_id,
                "actionName": "Approve",
                "options": {"comment": comments or "Approved via MCP"},
            }
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    f"{BASE_URL}/action",
                    headers=headers,
                    params={
                        "realm": client.realm,
                        "user": user,
                        "passwordAdapter": password_adapter,
                    },
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_reject_sourcing_task",
        description=(
            "Reject/deny a sourcing task in Ariba with comments. "
            "Requires user and password_adapter for user-context auth."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def reject_sourcing_task(
        approval_id: str,
        comments: str,
        user: str,
        password_adapter: str,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            headers["Content-Type"] = "application/json"
            payload = {
                "actionableType": "Task",
                "uniqueName": approval_id,
                "actionName": "Deny",
                "options": {"comment": comments},
            }
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    f"{BASE_URL}/action",
                    headers=headers,
                    params={
                        "realm": client.realm,
                        "user": user,
                        "passwordAdapter": password_adapter,
                    },
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)
