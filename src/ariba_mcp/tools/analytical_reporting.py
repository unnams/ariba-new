"""Analytical Reporting API for Strategic Procurement and Operational Procurement.

SAP Ariba API: Analytical Reporting API
Docs: https://help.sap.com/docs/ariba-apis
Developer Portal: https://developer.ariba.com (search "Analytical Reporting API")

Endpoint patterns:
  Sync views:  GET  {base}/analytics-reporting-details/v1/prod/views/{viewName}?realm={realm}&filters={json}
  View count:  GET  {base}/analytics-reporting-details/v1/prod/views/{viewName}/count?realm={realm}
  Submit job:  POST {base}/analytics-reporting-job/v1/prod/jobs
  Job status:  GET  {base}/analytics-reporting-job/v1/prod/jobs/{jobId}
  Job results: GET  {base}/analytics-reporting-jobresult/v1/prod/jobs/{jobId}

Authentication: OAuth 2.0 Bearer token + apiKey header (handled by client.py)
Pagination: pageToken in response body
"""

import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

SYNC_API = "analytics-reporting-details/v1/prod"
JOB_API = "analytics-reporting-job/v1/prod"
JOB_RESULT_API = "analytics-reporting-jobresult/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register Analytical Reporting tools."""

    # ── EXAMPLE TOOL (fully implemented) ──────────────────────────────

    @mcp.tool(
        name="ariba_analytics_query_view",
        description=(
            "Query an analytical reporting view (synchronous). "
            "Returns procurement analytics data. "
            "Pass filters as JSON string, e.g. "
            "'{\"createdDateFrom\":\"2025-01-01\",\"createdDateTo\":\"2025-01-31\"}'."
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
            result = await client.fetch_view(SYNC_API, view_name, filter_dict, page_token)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    # ── TODO: Implement these tools ───────────────────────────────────
    #
    # 1. ariba_analytics_count_view
    #    - Get record count for an analytical view
    #    - Use: client.fetch_view_count(SYNC_API, view_name, filters)
    #
    # 2. ariba_analytics_submit_job
    #    - Submit async analytics job for large datasets
    #    - Use: client.submit_job(JOB_API, view_name, filters)
    #    - Returns jobId
    #
    # 3. ariba_analytics_get_job_status
    #    - Check async job status
    #    - Use: client.get_job_status(JOB_API, job_id)
    #
    # 4. ariba_analytics_get_job_results
    #    - Fetch results of completed async job
    #    - Use: client.get_job_results(JOB_RESULT_API, job_id, page_token)
    #
    # Copy the example tool pattern above for each new tool.
