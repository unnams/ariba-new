"""Contract Compliance API and Contract Workspace APIs for SAP Ariba.

Covers:
- Contract Compliance API:            contract-compliance/v1/prod
- Contract Workspace Retrieval API:   contract-workspace/v1/prod
- Contract Workspace Management APIs: contract-workspace-management/v1/prod
- Contract Terms Management API:      contract-terms/v1/prod

Docs: https://help.sap.com/docs/ariba-apis
"""

import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

COMPLIANCE_API = "contract-compliance/v1/prod"
WORKSPACE_API = "contract-workspace/v1/prod"
TERMS_API = "contract-terms/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register Contract Compliance and Workspace tools."""

    @mcp.tool(
        name="ariba_contract_list_workspaces",
        description="List contract workspaces. Returns contract workspace summaries with status, dates, and parties.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_workspaces(page_token: str | None = None) -> str:
        try:
            params = {}
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(WORKSPACE_API, "workspaces", params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_contract_get_workspace",
        description="Get full details of a contract workspace by its ID.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_workspace(workspace_id: str) -> str:
        try:
            result = await client.fetch_resource(WORKSPACE_API, f"workspaces/{workspace_id}")
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_contract_check_compliance",
        description="Check contract compliance status. Returns compliance data for contracts in the realm.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def check_compliance(page_token: str | None = None) -> str:
        try:
            params = {}
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(COMPLIANCE_API, "contracts", params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_contract_get_compliance",
        description="Get compliance details for a specific contract by ID.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_compliance(contract_id: str) -> str:
        try:
            result = await client.fetch_resource(COMPLIANCE_API, f"contracts/{contract_id}")
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_contract_get_terms",
        description="Get terms and conditions for a specific contract.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_terms(contract_id: str) -> str:
        try:
            result = await client.fetch_resource(TERMS_API, f"contracts/{contract_id}/terms")
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)
