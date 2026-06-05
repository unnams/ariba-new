from fastmcp import FastMCP

from ariba_mcp.client import AribaClient


def register(mcp: FastMCP, client: AribaClient) -> None:
    from ariba_mcp.tools.procurement import (
        audit_search,
        contract_compliance,
        contract_terms_management,
        document_approval,
        integration_monitoring_for_procurement,
        operational_reporting_for_procurement,
        procurement_workspace,
    )

    document_approval.register(mcp, client)
    audit_search.register(mcp, client)
    contract_compliance.register(mcp, client)
    contract_terms_management.register(mcp, client)
    integration_monitoring_for_procurement.register(mcp, client)
    procurement_workspace.register(mcp, client)
    operational_reporting_for_procurement.register(mcp, client)
