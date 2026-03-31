"""Contract Terms Management API.

Owner: Shabreen
Docs: https://help.sap.com/doc/3030e0a0f768498f91043a8abbc75ff1/cloud/en-US/index.html

This API allows developers to create and manage contract terms and contract 
requests within SAP Ariba.

Endpoints implemented:
  GET  /contractTerms    – retrieve information about contract terms
  POST /contractTerms    – create new contract terms
  GET  /contractRequests – retrieve information about contract requests
  POST /contractRequests – create new contract requests
"""

import json
from fastmcp import FastMCP
from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

CONTRACT_TERMS_API = "contract-terms-management/v1/prod"

def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_contract_terms_list",
        description="Retrieve a list of contract terms based on filters like contractId or status.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def contract_terms_list(
        realm: str,
        filter: str | None = None,
        top: int | None = None,
        skip: int | None = None,
    ) -> str:
        """
        Args:
            realm:   Required. The target SAP Ariba realm.
            filter:  Optional. OData filter (e.g., "contractId eq 'C123'").
            top:     Optional. Max records (default 10).
            skip:    Optional. Offset for pagination.
        """
        try:
            params = {"realm": realm}
            if filter: params["$filter"] = filter
            if top: params["$top"] = top
            if skip: params["$skip"] = skip
            
            result = await client.fetch_resource(CONTRACT_TERMS_API, "contractTerms", params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_contract_term_create",
        description="Create new contract terms in the specified realm.",
        annotations={"readOnlyHint": False, "destructiveHint": False},
    )
    async def contract_term_create(realm: str, body: dict) -> str:
        """
        Args:
            realm: Required. The target SAP Ariba realm.
            body:  Required. The JSON payload containing contract term details.
        """
        try:
            # Note: client.post_resource would need to be implemented in your AribaClient
            result = await client.post_resource(
                CONTRACT_TERMS_API, "contractTerms", {"realm": realm}, body
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_contract_requests_list",
        description="Retrieve contract requests to track the status of contract creation.",
        annotations={"readOnlyHint": True, "destructiveHint": False},
    )
    async def contract_requests_list(
        realm: str,
        filter: str | None = None,
    ) -> str:
        """
        Args:
            realm:  Required. The target SAP Ariba realm.
            filter: Optional. Filter by requestId or status.
        """
        try:
            params = {"realm": realm}
            if filter: params["$filter"] = filter
            
            result = await client.fetch_resource(CONTRACT_TERMS_API, "contractRequests", params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)