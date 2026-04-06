import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

CONTRACT_TERMS_API = "contract-terms-management/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_contract_terms_get",
        description=(
            "Retrieve contract terms for a specific contract workspace from SAP Ariba. "
            "Returns the contract terms document associated with the given contract workspace ID."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def contract_terms_get(
        realm: str,
        contract_id: str,
        top: int | None = None,
        skip: int | None = None,
    ) -> str:
        try:
            params: dict = {"realm": realm}
            if top is not None:
                params["$top"] = top
            if skip is not None:
                params["$skip"] = skip
            result = await client.fetch_resource(
                CONTRACT_TERMS_API,
                f"contractWorkspaces/{contract_id}/contractTerms",
                params,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_contract_terms_create",
        description=(
            "Create a new contract terms document in a specific contract workspace in SAP Ariba. "
            "Also creates a corresponding contract request in SAP Ariba Procurement solutions. "
            "The contract workspace must already exist before calling this tool."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
    )
    async def contract_terms_create(
        realm: str,
        contract_id: str,
        body: dict,
    ) -> str:
        try:
            result = await client.post_resource(
                CONTRACT_TERMS_API,
                f"contractWorkspaces/{contract_id}/contractTerms",
                {"realm": realm},
                body,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_contract_requests_list",
        description=(
            "Retrieve a list of contract requests from SAP Ariba. "
            "Supports filtering by requestId, status, or other OData filter fields."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def contract_requests_list(
        realm: str,
        filter: str | None = None,
        top: int | None = None,
        skip: int | None = None,
    ) -> str:
        try:
            params: dict = {"realm": realm}
            if filter:
                params["$filter"] = filter
            if top is not None:
                params["$top"] = top
            if skip is not None:
                params["$skip"] = skip
            result = await client.fetch_resource(
                CONTRACT_TERMS_API, "contractRequests", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_contract_request_create",
        description=(
            "Create a new contract request in SAP Ariba Procurement solutions. "
            "Use this to import contract request header details directly into the procurement solution."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
    )
    async def contract_request_create(
        realm: str,
        body: dict,
    ) -> str:
        try:
            result = await client.post_resource(
                CONTRACT_TERMS_API,
                "contractRequests",
                {"realm": realm},
                body,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)
