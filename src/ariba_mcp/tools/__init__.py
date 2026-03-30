"""Tool registration for all SAP Ariba API domains.

8 domain modules covering 48 SAP Ariba APIs:
https://help.sap.com/docs/ariba-apis
"""

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.tools import (
    administration,
    catalogs,
    contracts,
    procurement_reporting,
    purchase_orders,
    sourcing,
    supplier_management,
    supply_chain,
)

_DOMAINS = [
    supplier_management,
    procurement_reporting,
    sourcing,
    contracts,
    purchase_orders,
    catalogs,
    supply_chain,
    administration,
]


def register_all_tools(mcp: FastMCP, client: AribaClient) -> None:
    """Register tools from every domain module."""
    for domain in _DOMAINS:
        domain.register(mcp, client)
