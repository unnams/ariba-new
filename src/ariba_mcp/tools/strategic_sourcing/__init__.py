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
    from ariba_mcp.tools.strategic_sourcing import master_data  
    from ariba_mcp.tools.strategic_sourcing import product_sourcing
    from ariba_mcp.tools.strategic_sourcing import external_approval_API
    from ariba_mcp.tools.strategic_sourcing import sourcing_project_mangement

    _example.register(mcp, client)
    master_data.register(mcp, client)
    product_sourcing.register(mcp, client)
    external_approval_API.register(mcp, client)
    sourcing_project_mangement.register(mcp, client)  

       

    # As team members add files, import and register them here:
    # from ariba_mcp.tools.strategic_sourcing import sourcing_project_management
    # sourcing_project_management.register(mcp, client)
 
