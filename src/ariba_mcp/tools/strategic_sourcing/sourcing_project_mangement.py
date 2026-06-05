import json

from fastmcp import FastMCP
from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_profile_settings
from ariba_mcp.errors import handle_ariba_error

SOURCING_PROJECT_API = "https://openapi.ariba.com/api/sourcing-project-management/v2/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_list_sourcing_projects",
        description=(
            "Retrieve list of sourcing projects from Ariba. "
            "Used to view sourcing events, RFQs, and project details."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def list_sourcing_projects(
        user: str | None = None,
        password_adapter: str | None = None,
        filter_expr: str | None = None,
        page_token: str | None = None,
    ) -> str:
        try:
            active_client = AribaClient(get_profile_settings("SAPI"))
            effective_user = user or active_client._settings.ariba_user
            effective_adapter = password_adapter or active_client._settings.ariba_password_adapter
            if not effective_user or not effective_adapter:
                return json.dumps(
                    {
                        "error": True,
                        "message": (
                            "Missing required query params for this API. "
                            "Provide `user` and `password_adapter`, or set "
                            "ARIBA_SAPI_USER and ARIBA_SAPI_PASSWORD_ADAPTER in .env."
                        ),
                    }
                )

            if not filter_expr:
                return json.dumps(
                    {
                        "error": True,
                        "message": (
                            "This API requires a valid `$filter` expression. "
                            "Pass `filter_expr` exactly as defined in your Ariba "
                            "Sourcing Project Management API docs for your tenant."
                        ),
                    }
                )

            result = await active_client.fetch(
                f"{SOURCING_PROJECT_API}/projects",
                params={
                    "user": effective_user,
                    "passwordAdapter": effective_adapter,
                    "$filter": filter_expr,
                    "pageToken": page_token,
                },
            )

            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)


    @mcp.tool(
        name="ariba_get_sourcing_project",
        description=(
            "Retrieve details of a specific sourcing project using project ID."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_sourcing_project(
        project_id: str,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            active_client = AribaClient(get_profile_settings("SAPI"))
            effective_user = user or active_client._settings.ariba_user
            effective_adapter = password_adapter or active_client._settings.ariba_password_adapter
            if not effective_user or not effective_adapter:
                return json.dumps(
                    {
                        "error": True,
                        "message": (
                            "Missing required query params for this API. "
                            "Provide `user` and `password_adapter`, or set "
                            "ARIBA_SAPI_USER and ARIBA_SAPI_PASSWORD_ADAPTER in .env."
                        ),
                    }
                )
            result = await active_client.fetch(
                f"{SOURCING_PROJECT_API}/projects/{project_id}",
                params={
                    "user": effective_user,
                    "passwordAdapter": effective_adapter,
                },
            )

            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)


    @mcp.tool(
        name="ariba_create_sourcing_project",
        description=(
            "Create a new sourcing project in Ariba. "
            "Provide project details in JSON format."
        ),
        annotations={
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def create_sourcing_project(
        project_data: str,
        user: str | None = None,
        password_adapter: str | None = None,
    ) -> str:
        try:
            active_client = AribaClient(get_profile_settings("SAPI"))
            payload = json.loads(project_data)
            effective_user = user or active_client._settings.ariba_user
            effective_adapter = password_adapter or active_client._settings.ariba_password_adapter
            if not effective_user or not effective_adapter:
                return json.dumps(
                    {
                        "error": True,
                        "message": (
                            "Missing required query params for this API. "
                            "Provide `user` and `password_adapter`, or set "
                            "ARIBA_SAPI_USER and ARIBA_SAPI_PASSWORD_ADAPTER in .env."
                        ),
                    }
                )

            result = await active_client.post(
                f"{SOURCING_PROJECT_API}/projects",
                json=payload,
                params={
                    "user": effective_user,
                    "passwordAdapter": effective_adapter,
                },
            )

            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)
