"""Supply Chain & Network APIs.

APIs in this module:
  1. Ship Notice API for Buyers                     — Owner: Ayub
     Docs: https://help.sap.com/doc/2fb0ec8cde534b028e64b9d45378ad8a/cloud/en-US/index.html
  2. Ship Notice API for Suppliers                  — Owner: Shabreen
     Docs: https://help.sap.com/doc/5e5dbefd5c02432298d2a5ec45805b95/cloud/en-US/index.html
  3. Planning Collaboration Buyer API               — Owner: Anim
     Docs: https://help.sap.com/doc/c2f36577439842ae9e96c79f4a1e6df8/cloud/en-US/index.html
  4. Planning Collaboration Supplier API            — Owner: Shabreen
     Docs: https://help.sap.com/doc/debc8145f35b4db686e9748d29a9a453/cloud/en-US/index.html
  5. Proof of Service API for Buyers                — Owner: (unassigned)
     Docs: https://help.sap.com/doc/ef5ee22f9e9e4777ba7b5c7597681a0f/cloud/en-US/index.html
  6. Ariba Network Invoice Header Data Extraction   — Owner: Ayub
     Docs: https://help.sap.com/doc/9e361d7c0ccc40f5840012785f249811/cloud/en-US/index.html
  7. Trading Partner Profile Certification API      — Owner: Ayub
     Docs: https://help.sap.com/doc/e4cbb9447e7e4e9ea469c5fb5fe5179b/cloud/en-US/index.html
  8. Data Replication Status for Multi-ERP           — Owner: Ayub
     Docs: https://help.sap.com/doc/6350dec774d9447b8ce1823a91ac698d/cloud/en-US/index.html

Developer Portal: https://developer.ariba.com
"""

import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

# ── API path constants ────────────────────────────────────────────────
# SHIP_NOTICE_BUYERS_API = "..."
# SHIP_NOTICE_SUPPLIERS_API = "..."
# PLANNING_COLLAB_BUYER_API = "..."
# PLANNING_COLLAB_SUPPLIER_API = "..."
# PROOF_OF_SERVICE_BUYERS_API = "..."
# INVOICE_HEADER_EXTRACTION_API = "..."
# TRADING_PARTNER_CERT_API = "..."
# DATA_REPLICATION_STATUS_API = "..."


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register Supply Chain & Network tools."""

    # ── EXAMPLE TOOL ──────────────────────────────────────────────────

    @mcp.tool(
        name="ariba_invoice_header_list",
        description=(
            "List invoice headers from Ariba Network. "
            "Get header information of invoices associated with a Business Network user ID (ANID)."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def invoice_header_list(anid: str, page_token: str | None = None) -> str:
        try:
            # TODO: Replace with actual API path from Developer Portal
            api_path = "invoice-header-extraction/v1/prod"
            params = {"anid": anid}
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(api_path, "invoices", params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    # ── TODO: Implement these APIs ────────────────────────────────────
    #
    # 1. Ship Notice API for Buyers (Ayub)
    #    - Retrieve ship-notice info from Business Network (buyer side)
    #
    # 2. Ship Notice API for Suppliers (Shabreen)
    #    - Retrieve ship-notice info (supplier side)
    #
    # 3. Planning Collaboration Buyer API (Anim)
    #    - Retrieve planning info from Business Network (buyer side)
    #
    # 4. Planning Collaboration Supplier API (Shabreen)
    #    - Retrieve planning info (supplier side)
    #
    # 5. Proof of Service API for Buyers (unassigned)
    #    - Track service delivery proof
    #
    # 6. Trading Partner Profile Certification API (Ayub)
    #    - Retrieve supplier certifications, download cert files
    #
    # 7. Data Replication Status for Multi-ERP (Ayub)
    #    - Retrieve status of data replication across ERPs
