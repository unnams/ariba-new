"""Business Network APIs.

APIs in this folder:
  - Ariba Network Purchase Orders API (Anil)
  - Purchase Orders Supplier API (Nitish SM)
  - Order Change Requests API for Buyers (Anim)
  - Order Change Requests API for Suppliers (Shabreen)
  - Ariba Network Invoice Header Data Extraction API (Ayub)
  - Ship Notice API for Buyers (Ayub)
  - Ship Notice API for Suppliers (Shabreen)
  - Planning Collaboration Buyer API (Anim)
  - Planning Collaboration Supplier API (Shabreen)
  - Trading Partner Profile Certification API (Ayub)
  - Supplier Information API (Shabreen)
  - Proof of Service API for Buyers (unassigned)
  - Data Replication Status for Multi-ERP (Ayub)
  - Transaction Monitoring API (Anim)

Each person creates their own .py file in this folder.
"""

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register all Business Network tools from submodules."""
    from ariba_mcp.tools.business_network import _example
    _example.register(mcp, client)

    # ✅ Correctly inside register() so mcp and client are in scope
    from ariba_mcp.tools.business_network import order_change_requests_for_suppliers
    order_change_requests_for_suppliers.register(mcp, client)

    #connecting the tool of planning Collaboration Supplier API
    from ariba_mcp.tools.business_network import ship_notice_for_suppliers
    ship_notice_for_suppliers.register(mcp, client)
    #connecting the tool of planning Collaboration Supplier API
    from ariba_mcp.tools.business_network import planning_collaboration_supplier
    planning_collaboration_supplier.register(mcp, client)
    # #connecting the tool of Supplier Information API
    from ariba_mcp.tools.business_network import supplier_information
    supplier_information.register(mcp, client)