from fastmcp import FastMCP

from ariba_mcp.client import AribaClient


def register(mcp: FastMCP, client: AribaClient) -> None:
    from ariba_mcp.tools.general import Integration_monitoring_API, asset_management, user_qualification

    Integration_monitoring_API.register(mcp, client)
    asset_management.register(mcp, client)
    user_qualification.register(mcp, client)
