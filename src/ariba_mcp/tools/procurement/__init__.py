"""Procurement APIs.

APIs in this folder:
  - Operational Reporting API for Procurement (Vanshika)
  - Analytical Reporting API for Strategic & Operational Procurement (Anim)
  - Contract Compliance API (Vanshika)
  - Contract Workspace Retrieval API (Anim)
  - Contract Workspace Management APIs (Rohit Naik)
  - Contract Terms Management API (Shabreen)
  - Cost Breakdown Data Extraction API (Vanshika)

Each person creates their own .py file in this folder.
"""

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register all Procurement tools from submodules."""
    from ariba_mcp.tools.procurement import _example

    _example.register(mcp, client)

    # As team members add files, import and register them here:
    # from ariba_mcp.tools.procurement import analytical_reporting
    # analytical_reporting.register(mcp, client)
    from ariba_mcp.tools.procurement import contract_terms_management
    contract_terms_management.register(mcp, client)