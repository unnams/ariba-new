"""Supplier Management APIs.

APIs in this folder:
  - Supplier Data API with Pagination (Nitish SM)
  - Supplier Data API (Nitish SM)
  - Supplier Data Extraction API (Nitish SM)
  - Ariba Network Supplier Profile API (Nitish SM)
  - Supplier Invite API (Nitish SM)
  - Supplier Risk Engagements API (Nitish SM)
  - Risk Exposure API (Anim)
  - Risk Category Information API (Shabreen)

Each person creates their own .py file in this folder.
"""

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register all Supplier Management tools from submodules."""
    from ariba_mcp.tools.supplier_management import _example, supplier_data_paginated

    _example.register(mcp, client)
    supplier_data_paginated.register(mcp, client)

    # As team members add files, import and register them here:
    # from ariba_mcp.tools.supplier_management import supplier_data_extraction
    # supplier_data_extraction.register(mcp, client)
