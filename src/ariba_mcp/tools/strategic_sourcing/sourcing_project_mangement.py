import json

import httpx
from fastmcp import FastMCP

from ariba_mcp.auth import DirectAuthClient
from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_settings
from ariba_mcp.errors import handle_ariba_error

BASE_URL = "https://openapi.ariba.com/api/sourcing-project-management/v2/prod"


def _make_auth() -> DirectAuthClient:
    s = get_settings()
    return DirectAuthClient(
        client_id=s.sourcing_pm_client_id,
        client_secret=s.sourcing_pm_client_secret,
        api_key=s.sourcing_pm_api_key,
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
        name="ariba_list_sourcing_projects",
        description=(
            "List sourcing projects from Ariba (RFQs, RFPs, events). "
            "filter_expr is OData syntax — e.g. "
            "\"(createDateFrom gt 1704067200000 and createDateTo lt 1767225600000)\". "
            "user and password_adapter are optional and default to .env values."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_sourcing_projects(
        filter_expr: str,
        user: str | None = None,
        password_adapter: str | None = None,
        page_token: str | None = None,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            params = _user_params(client.realm, user, password_adapter)
            params["$filter"] = filter_expr
            if page_token:
                params["pageToken"] = page_token
            async with httpx.AsyncClient() as http:
                resp = await http.get(f"{BASE_URL}/projects", headers=headers, params=params, timeout=60)
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_get_sourcing_project",
        description=(
            "Get details of a specific sourcing project by project ID (e.g. 'WS5396278319'). "
            "Returns full project details including events, participants, and timeline."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_sourcing_project(
        project_id: str,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            params = _user_params(client.realm, user, password_adapter)
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/projects/{project_id}",
                    headers=headers, params=params, timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_get_sourcing_project_documents",
        description=(
            "Retrieve documents linked to a sourcing project (RFx, contracts, attachments). "
            "filter_expr is OData syntax — e.g. "
            "\"(createDateFrom gt 1704067200000 and createDateTo lt 1767225600000)\"."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_sourcing_project_documents(
        project_id: str,
        filter_expr: str | None = None,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            params = _user_params(client.realm, user, password_adapter)
            if filter_expr:
                params["$filter"] = filter_expr
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/projects/{project_id}/documents",
                    headers=headers, params=params, timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_get_sourcing_project_team",
        description=(
            "Retrieve team / project group members of a sourcing project. "
            "team_id is the project group ID (e.g. 'PG5396278322'). "
            "filter_expr is optional OData syntax."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_sourcing_project_team(
        project_id: str,
        team_id: str,
        filter_expr: str | None = None,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            params = _user_params(client.realm, user, password_adapter)
            if filter_expr:
                params["$filter"] = filter_expr
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/projects/{project_id}/teams/{team_id}",
                    headers=headers, params=params, timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_get_sourcing_project_history",
        description=(
            "Retrieve history records (audit trail) for a sourcing project — "
            "state changes, approvals, edits, and other lifecycle events."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_sourcing_project_history(
        project_id: str,
        filter_expr: str | None = None,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            params = _user_params(client.realm, user, password_adapter)
            if filter_expr:
                params["$filter"] = filter_expr
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/projects/{project_id}/historyRecords",
                    headers=headers, params=params, timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_get_sourcing_project_tasks",
        description=(
            "Retrieve tasks of a sourcing project (approvals, to-dos, milestones). "
            "filter_expr is optional OData syntax."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_sourcing_project_tasks(
        project_id: str,
        filter_expr: str | None = None,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            headers = await _auth.get_headers()
            params = _user_params(client.realm, user, password_adapter)
            if filter_expr:
                params["$filter"] = filter_expr
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/projects/{project_id}/tasks",
                    headers=headers, params=params, timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)
