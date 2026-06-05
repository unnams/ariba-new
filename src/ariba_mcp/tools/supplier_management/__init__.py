from fastmcp import FastMCP

from ariba_mcp.client import AribaClient


def register(mcp: FastMCP, client: AribaClient) -> None:
    from ariba_mcp.tools.supplier_management import (
        bank_validation,
        risk_category_information,
        supplier_data_api,
        supplier_data_paginated,
        supplier_invite,
        supplier_risk_engagements,
    )

    supplier_data_paginated.register(mcp, client)
    supplier_data_api.register(mcp, client)
    supplier_invite.register(mcp, client)
    supplier_risk_engagements.register(mcp, client)
    risk_category_information.register(mcp, client)
    bank_validation.register(mcp, client)
