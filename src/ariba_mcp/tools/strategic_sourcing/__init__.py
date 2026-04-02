"""Strategic Sourcing APIs.

APIs in this folder:
  - Operational Reporting API for Strategic Sourcing (Pranathi)
  - Sourcing Project Management API (Pranathi)
  - Event Management API (Anim)
  - External Approval API for Sourcing & Supplier Mgmt (Pranathi)
  - Master Data Retrieval API for Sourcing (Pranathi)
  - Pricing API for Product Sourcing (Pranathi)
  - Surrogate Bid API (Rohit Naik)
  - Product Hierarchy Management API (Shabreen)
  - Bill of Materials Import API (Anim)

Each person creates their own .py file in this folder.
"""

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register all Strategic Sourcing tools from submodules."""
    from ariba_mcp.tools.strategic_sourcing import _example

    _example.register(mcp, client)

    # As team members add files, import and register them here:
    from ariba_mcp.tools.strategic_sourcing import surrogate_bid
    surrogate_bid.register(mcp, client)
