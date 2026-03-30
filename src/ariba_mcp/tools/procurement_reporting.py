"""Procurement Reporting APIs.

APIs in this module:
  1. Operational Reporting API for Procurement       — Owner: Vanshika
     Docs: https://help.sap.com/doc/42cb9e6fb65a4fa7b03f5e0ec7d406f9/cloud/en-US/index.html
  2. Analytical Reporting API (Strategic & Operational) — Owner: Anim
     Docs: https://help.sap.com/doc/bf0cde439a0142fbbaf511bfac5b594d/cloud/en-US/index.html

Endpoint patterns (Operational Reporting for Procurement):
  Sync:  GET  {base}/procurement-reporting-details/v1/prod/views/{viewName}?realm={realm}&filters={json}
  Count: GET  {base}/procurement-reporting-details/v1/prod/views/{viewName}/count?realm={realm}
  Meta:  GET  {base}/procurement-reporting-view/v2/prod/viewTemplates
  Job:   POST {base}/procurement-reporting-job/v2/prod/jobs
  Job:   GET  {base}/procurement-reporting-jobresult/v2/prod/jobs/{jobId}

Endpoint patterns (Analytical Reporting):
  Sync:  GET  {base}/analytics-reporting-details/v1/prod/views/{viewName}?realm={realm}&filters={json}
  Job:   POST {base}/analytics-reporting-job/v1/prod/jobs
  Job:   GET  {base}/analytics-reporting-jobresult/v1/prod/jobs/{jobId}

Common procurement views: POLineItemSystemView, RequisitionLineItemSystemView,
  InvoiceLineItemSystemView, ReceiptSystemView, PaymentSystemView,
  ContractLineItemSystemView, CostCenterProcurementSystemView, SupplierSystemView

Developer Portal: https://developer.ariba.com
"""

import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

# ── API path constants ────────────────────────────────────────────────
PROCUREMENT_SYNC_API = "procurement-reporting-details/v1/prod"
PROCUREMENT_META_API = "procurement-reporting-view/v2/prod"
PROCUREMENT_JOB_API = "procurement-reporting-job/v2/prod"
PROCUREMENT_RESULT_API = "procurement-reporting-jobresult/v2/prod"
ANALYTICS_SYNC_API = "analytics-reporting-details/v1/prod"
ANALYTICS_JOB_API = "analytics-reporting-job/v1/prod"
ANALYTICS_RESULT_API = "analytics-reporting-jobresult/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register Procurement Reporting tools."""

    # ── EXAMPLE TOOL ──────────────────────────────────────────────────

    @mcp.tool(
        name="ariba_procurement_query_view",
        description=(
            "Query a procurement operational reporting view (synchronous). "
            "Common views: POLineItemSystemView, RequisitionLineItemSystemView, "
            "InvoiceLineItemSystemView, ReceiptSystemView, PaymentSystemView. "
            "Filters: '{\"createdDateFrom\":\"2025-01-01\",\"createdDateTo\":\"2025-01-31\"}'."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def procurement_query_view(
        view_name: str,
        filters: str | None = None,
        page_token: str | None = None,
    ) -> str:
        try:
            filter_dict = json.loads(filters) if filters else None
            result = await client.fetch_view(PROCUREMENT_SYNC_API, view_name, filter_dict, page_token)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    # ── TODO: Implement these tools ───────────────────────────────────
    #
    # --- Operational Reporting for Procurement (Vanshika) ---
    #
    # 1. ariba_procurement_list_views
    #    - client.fetch_resource(PROCUREMENT_META_API, "viewTemplates")
    #
    # 2. ariba_procurement_get_view_metadata
    #    - client.fetch_resource(PROCUREMENT_META_API, f"viewTemplates/{view_name}")
    #
    # 3. ariba_procurement_count_view
    #    - client.fetch_view_count(PROCUREMENT_SYNC_API, view_name, filters)
    #
    # 4. ariba_procurement_submit_job
    #    - client.submit_job(PROCUREMENT_JOB_API, view_name, filters)
    #
    # 5. ariba_procurement_get_job_status
    #    - client.get_job_status(PROCUREMENT_JOB_API, job_id)
    #
    # 6. ariba_procurement_get_job_results
    #    - client.get_job_results(PROCUREMENT_RESULT_API, job_id, page_token)
    #
    # --- Analytical Reporting (Anim) ---
    #
    # 7. ariba_analytics_query_view
    #    - client.fetch_view(ANALYTICS_SYNC_API, view_name, filters, page_token)
    #
    # 8. ariba_analytics_count_view
    #    - client.fetch_view_count(ANALYTICS_SYNC_API, view_name, filters)
    #
    # 9. ariba_analytics_submit_job
    #    - client.submit_job(ANALYTICS_JOB_API, view_name, filters)
    #
    # 10. ariba_analytics_get_job_status
    #     - client.get_job_status(ANALYTICS_JOB_API, job_id)
    #
    # 11. ariba_analytics_get_job_results
    #     - client.get_job_results(ANALYTICS_RESULT_API, job_id, page_token)
