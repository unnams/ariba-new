"""Operational Reporting API for Strategic Sourcing.

SAP Ariba API: Operational Reporting API for Strategic Sourcing
Docs: https://help.sap.com/docs/ariba-apis
Developer Portal: https://developer.ariba.com (search "Operational Reporting API for Strategic Sourcing")

Endpoint pattern:
  GET {base}/sourcing-reporting-view/v1/prod/views/{viewName}?realm={realm}&filters={json}

Common view templates:
  - SourcingProjectSourcingSystemView
  - SourcingRequestSourcingSystemView
  - EventItemSourcingSystemView
  - EventParticipationSourcingSystemView
  - ProjectAuditInfo_SpendOverview

Authentication: OAuth 2.0 Bearer token + apiKey header (handled by client.py)
Pagination: pageToken in response body
"""

import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

API_PATH = "sourcing-reporting-view/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register Operational Sourcing Reporting tools."""

    # ── EXAMPLE TOOL (fully implemented) ──────────────────────────────

    @mcp.tool(
        name="ariba_sourcing_query_view",
        description=(
            "Query a sourcing reporting view. "
            "Common views: SourcingProjectSourcingSystemView, SourcingRequestSourcingSystemView, "
            "EventItemSourcingSystemView. "
            "Filters example: '{\"createdDateFrom\":\"2025-01-01\",\"createdDateTo\":\"2025-01-31\"}'."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def query_view(
        view_name: str,
        filters: str | None = None,
        page_token: str | None = None,
    ) -> str:
        try:
            filter_dict = json.loads(filters) if filters else None
            result = await client.fetch_view(API_PATH, view_name, filter_dict, page_token)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    # ── TODO: Implement these tools ───────────────────────────────────
    #
    # 1. ariba_sourcing_count_view
    #    - Get record count for a sourcing view
    #    - Use: client.fetch_view_count(API_PATH, view_name, filters)
    #
    # 2. ariba_sourcing_list_projects
    #    - Shortcut: query SourcingProjectSourcingSystemView with date filters
    #    - Accept created_date_from, created_date_to as friendly params
    #
    # 3. ariba_sourcing_list_requests
    #    - Shortcut: query SourcingRequestSourcingSystemView with date filters
    #
    # Copy the example tool pattern above for each new tool.
