"""Purchase Order and Order Change APIs.

APIs in this module:
  1. Purchase Orders Supplier API            — Owner: Nitish SM
     Docs: https://help.sap.com/doc/8492ee96cb784a71a8e91c08c9634c95/cloud/en-US/index.html
  2. Ariba Network Purchase Orders API       — Owner: Anil
     Docs: https://help.sap.com/doc/0757c23390634ae7806f7fcd89d3d201/cloud/en-US/index.html
  3. Order Change Requests API for Buyers    — Owner: Anim
     Docs: https://help.sap.com/doc/41f6384c806f445a8f9e2f7c4464e5e7/cloud/en-US/index.html
  4. Order Change Requests API for Suppliers — Owner: Shabreen
     Docs: https://help.sap.com/doc/a18df06872cc41dab5617273313a23d4/cloud/en-US/index.html

Developer Portal: https://developer.ariba.com
"""

import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

# ── API path constants ────────────────────────────────────────────────
# PO_SUPPLIER_API = "..."
# PO_NETWORK_API = "..."
# ORDER_CHANGE_BUYERS_API = "..."
# ORDER_CHANGE_SUPPLIERS_API = "..."


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register Purchase Order tools."""

    # ── EXAMPLE TOOL ──────────────────────────────────────────────────

    @mcp.tool(
        name="ariba_po_network_list",
        description=(
            "List purchase orders from the Ariba Network Purchase Orders API (buyer perspective). "
            "Extract PO information from SAP Business Network."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def po_network_list(page_token: str | None = None) -> str:
        try:
            # TODO: Replace with actual API path from Developer Portal
            api_path = "network-purchase-orders/v1/prod"
            params = {}
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(api_path, "purchaseOrders", params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    # ── TODO: Implement these APIs ────────────────────────────────────
    #
    # 1. Purchase Orders Supplier API (Nitish SM)
    #    - Extract PO info from supplier perspective
    #
    # 2. Ariba Network Purchase Orders API — more tools (Anil)
    #    - Get single PO, search POs, line items
    #
    # 3. Order Change Requests API for Buyers (Anim)
    #    - Extract change request info (requires Business Network for Supply Chain)
    #
    # 4. Order Change Requests API for Suppliers (Shabreen)
    #    - Extract change request info from supplier perspective
