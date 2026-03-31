import json

from fastmcp import FastMCP
from ariba_mcp.client import AribaClient
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
        page_token: str | None = None,
    ) -> str:
        try:
            result = await client.fetch(
                f"{SOURCING_PROJECT_API}/projects",
                params={
                    "pageToken": page_token
                }
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
    ) -> str:
        try:
            result = await client.fetch(
                f"{SOURCING_PROJECT_API}/projects/{project_id}"
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
    ) -> str:
        try:
            payload = json.loads(project_data)

            result = await client.post(
                f"{SOURCING_PROJECT_API}/projects",
                json=payload
            )

            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)