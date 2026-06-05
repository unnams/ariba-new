from fastmcp import FastMCP

from ariba_mcp.client import AribaClient


def register(mcp: FastMCP, client: AribaClient) -> None:
    from ariba_mcp.tools.strategic_sourcing import (
        configuration_parameter_review,
        cost_breakdown_data_extraction,
        event_management,
        external_approval_API,
        master_data,
        product_hierarchy_management,
        product_sourcing,
        sourcing_project_mangement,
        surrogate_bid,
    )

    cost_breakdown_data_extraction.register(mcp, client)
    surrogate_bid.register(mcp, client)
    master_data.register(mcp, client)
    product_sourcing.register(mcp, client)
    product_hierarchy_management.register(mcp, client)
    configuration_parameter_review.register(mcp, client)
    sourcing_project_mangement.register(mcp, client)
    external_approval_API.register(mcp, client)
    event_management.register(mcp, client)
