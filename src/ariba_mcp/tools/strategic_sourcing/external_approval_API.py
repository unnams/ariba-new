import json

from fastmcp import FastMCP
from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

SOURCING_APPROVAL_API = "https://openapi.ariba.com/api/sourcing-approvals/v1/prod"


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
        page_token: str | None = None,
    ) -> str:
        try:
            result = await client.fetch(
                f"{SOURCING_APPROVAL_API}/approvals",
                params={
                    "pageToken": page_token
                }
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
    ) -> str:
        try:
            payload = {
                "action": "APPROVE",
                "comments": comments
                
                # Instead of:
# payload = {"action": "APPROVE", "comments": comments}

# # Do:
# payload = {"action": "APPROVE"}
# if comments:
#     payload["comments"] = comments
            }

            result = await client.post(
                f"{SOURCING_APPROVAL_API}/approvals/{approval_id}/actions",
                json=payload
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
    ) -> str:
        try:
            payload = {
                "action": "REJECT",
                "comments": comments
            }

            result = await client.post(
                f"{SOURCING_APPROVAL_API}/approvals/{approval_id}/actions",
                json=payload
            )

            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)