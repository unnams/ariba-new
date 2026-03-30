"""Contract APIs.

APIs in this module:
  1. Contract Compliance API              — Owner: Vanshika
     Docs: https://help.sap.com/doc/3ef7b70c268149288e4d59f43a94b68b/cloud/en-US/index.html
  2. Contract Workspace Retrieval API     — Owner: Anim
     Docs: https://help.sap.com/doc/d7a9abefbafa4a8ea8713480808d2480/cloud/en-US/index.html
  3. Contract Workspace Management APIs   — Owner: Rohit Naik
     Docs: https://help.sap.com/doc/21bc534709e140f880856e972203fb8d/cloud/en-US/index.html
  4. Contract Terms Management API        — Owner: Shabreen
     Docs: https://help.sap.com/doc/3030e0a0f768498f91043a8abbc75ff1/cloud/en-US/index.html
  5. NDA Data Export API                  — Owner: Rohit Naik
     Docs: https://help.sap.com/doc/2e309777da6d4abc872422a1d53ad7c1/cloud/en-US/index.html
  6. Cost Breakdown Data Extraction API   — Owner: Vanshika
     Docs: https://help.sap.com/doc/525b79f5d831496abfcd2bddd46626ad/cloud/en-US/index.html

Developer Portal: https://developer.ariba.com
"""

import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

# ── API path constants ────────────────────────────────────────────────
# Fill in exact paths from the Developer Portal.
# CONTRACT_COMPLIANCE_API = "..."
# CONTRACT_WORKSPACE_RETRIEVAL_API = "..."
# CONTRACT_WORKSPACE_MGMT_API = "..."
# CONTRACT_TERMS_API = "..."
# NDA_EXPORT_API = "..."
# COST_BREAKDOWN_API = "..."


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register Contract tools."""

    # ── EXAMPLE TOOL ──────────────────────────────────────────────────

    @mcp.tool(
        name="ariba_contract_compliance_list",
        description=(
            "List contract compliance data. "
            "Returns contract compliance status from the Contract Compliance API."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def contract_compliance_list(page_token: str | None = None) -> str:
        try:
            # TODO: Replace with actual API path from Developer Portal
            api_path = "contract-compliance/v1/prod"
            params = {}
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(api_path, "contracts", params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    # ── TODO: Implement these APIs ────────────────────────────────────
    #
    # 1. Contract Compliance API — get single contract, create/manage (Vanshika)
    #
    # 2. Contract Workspace Retrieval API (Anim)
    #    - Retrieve single workspace metadata (header fields)
    #    - Search workspaces by title, last modified date
    #
    # 3. Contract Workspace Management APIs (Rohit Naik)
    #    - Create, update, manage contract workspaces
    #
    # 4. Contract Terms Management API (Shabreen)
    #    - Create contract terms and contract requests
    #    - Retrieve info about terms and requests
    #
    # 5. NDA Data Export API (Rohit Naik)
    #    - Export transactional data related to non-disclosure agreements
    #
    # 6. Cost Breakdown Data Extraction API (Vanshika)
    #    - Search cost group documents
    #    - Download cost components and cost group terms
