"""Tool registration for all SAP Ariba API domains.

Domains map to the real SAP Ariba Developer Portal API categories:
https://help.sap.com/docs/ariba-apis
"""

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.tools import (
    analytical_reporting,
    contract_compliance,
    document_approval,
    operational_procurement,
    operational_sourcing,
    sourcing_project,
    supplier_data,
    supplier_risk,
)

_DOMAINS = [
    operational_procurement,
    operational_sourcing,
    analytical_reporting,
    supplier_data,
    contract_compliance,
    sourcing_project,
    document_approval,
    supplier_risk,
]


def register_all_tools(mcp: FastMCP, client: AribaClient) -> None:
    """Register tools from every domain module."""
    for domain in _DOMAINS:
        domain.register(mcp, client)
