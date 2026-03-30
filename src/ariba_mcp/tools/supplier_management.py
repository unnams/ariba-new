"""Supplier Management APIs.

APIs in this module:
  1. Supplier Data API with Pagination   — Owner: Nitish SM
     Docs: https://help.sap.com/doc/60ec8b8bb9344dbe8dcf15e2a1edc85b/cloud/en-US/index.html
  2. Supplier Data API                   — Owner: Nitish SM
     Docs: https://help.sap.com/doc/ae35ad2426d54acca48272f08dbfbe73/cloud/en-US/index.html
  3. Supplier Data Extraction API        — Owner: Nitish SM
     Docs: https://help.sap.com/doc/0dfbbe78ddb647628f4b0acb3afe723d/cloud/en-US/index.html
  4. Ariba Network Supplier Profile API  — Owner: Nitish SM
     Docs: https://help.sap.com/doc/bba3a69a443a46ee80382c8d8c0610ae/cloud/en-US/index.html
  5. Supplier Invite API                 — Owner: Nitish SM
     Docs: https://help.sap.com/doc/8903b23ba81845efb4760ba9ad2096bb/cloud/en-US/index.html
  6. Supplier Information API            — Owner: Shabreen
     Docs: https://help.sap.com/doc/8755ad14edb74721a039337c0c01edf2/cloud/en-US/index.html
  7. Supplier Risk Engagements API       — Owner: Nitish SM
     Docs: https://help.sap.com/doc/892703b130354abbb5013c3587a08cb2/cloud/en-US/index.html
  8. Risk Exposure API                   — Owner: Anim
     Prod URL: https://openapi.ariba.com/api/risk-exposure/v3/prod
     Docs: https://help.sap.com/doc/2e493ebf33de4b2bb813c8de0fb9ed9b/cloud/en-US/index.html
  9. Risk Category Information API       — Owner: Shabreen
     Docs: https://help.sap.com/doc/3a9efde5fd074398b9ae284a478f98e4/cloud/en-US/index.html

Developer Portal: https://developer.ariba.com
"""

import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

# ── API path constants ────────────────────────────────────────────────
# Fill in exact paths from the Developer Portal as you implement each API.
RISK_EXPOSURE_API = "risk-exposure/v3/prod"
# SUPPLIER_DATA_PAGINATED_API = "..."
# SUPPLIER_DATA_API = "..."
# SUPPLIER_DATA_EXTRACTION_API = "..."
# SUPPLIER_PROFILE_API = "..."
# SUPPLIER_INVITE_API = "..."
# SUPPLIER_INFO_API = "..."
# SUPPLIER_RISK_ENGAGEMENTS_API = "..."
# RISK_CATEGORY_API = "..."


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register Supplier Management tools."""

    # ── EXAMPLE TOOL ──────────────────────────────────────────────────

    @mcp.tool(
        name="ariba_risk_get_exposure",
        description=(
            "Get supplier risk exposure data. Pass an SM vendor ID or ERP vendor ID "
            "to retrieve the supplier's overall and category risk scores."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def risk_get_exposure(vendor_id: str) -> str:
        try:
            result = await client.fetch_resource(RISK_EXPOSURE_API, f"riskExposure/{vendor_id}")
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    # ── TODO: Implement these APIs ────────────────────────────────────
    #
    # 1. Supplier Data API with Pagination (Nitish SM)
    #    - Retrieve/update supplier info (registration, qualification, preferred status)
    #
    # 2. Supplier Data API (Nitish SM)
    #    - Extract supplier data including questionnaire details
    #
    # 3. Supplier Data Extraction API (Nitish SM)
    #    - Retrieve data about specific suppliers from a specific realm
    #
    # 4. Ariba Network Supplier Profile API (Nitish SM)
    #    - Retrieve supplier profile info based on ANID
    #
    # 5. Supplier Invite API (Nitish SM)
    #    - Create vendor records in SAP Business Network
    #
    # 6. Supplier Information API (Shabreen)
    #    - Determine if buyer-supplier relationship exists on Business Network
    #
    # 7. Supplier Risk Engagements API (Nitish SM)
    #    - Get engagement risk assessment project data (engagements, issues, questionnaires)
    #
    # 8. Risk Category Information API (Shabreen)
    #    - Add supplier level data to suppliers monitored in risk profiles
