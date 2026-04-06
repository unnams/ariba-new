from fastmcp import FastMCP

from ariba_mcp.client import AribaClient


def register(mcp: FastMCP, client: AribaClient) -> None:
    from ariba_mcp.tools.business_network import (
        data_replication_status,
        order_change_requests_for_suppliers,
        planning_collaboration_supplier,
        ship_notice_for_suppliers,
        supplier_information,
    )

    data_replication_status.register(mcp, client)
    supplier_information.register(mcp, client)
    order_change_requests_for_suppliers.register(mcp, client)
    planning_collaboration_supplier.register(mcp, client)
    ship_notice_for_suppliers.register(mcp, client)
