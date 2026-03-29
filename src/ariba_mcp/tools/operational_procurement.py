"""Operational Reporting API for Procurement.

SAP Ariba API: Operational Reporting API for Procurement
Docs: https://help.sap.com/docs/ariba-apis
Developer Portal: https://developer.ariba.com (search "Operational Reporting API for Procurement")

Endpoint patterns:
  Sync views:   GET  {base}/procurement-reporting-details/v1/prod/views/{viewName}?realm={realm}&filters={json}
  View count:   GET  {base}/procurement-reporting-details/v1/prod/views/{viewName}/count?realm={realm}
  View metadata:GET  {base}/procurement-reporting-view/v2/prod/viewTemplates
  Submit job:   POST {base}/procurement-reporting-job/v2/prod/jobs
  Job status:   GET  {base}/procurement-reporting-job/v2/prod/jobs/{jobId}
  Job results:  GET  {base}/procurement-reporting-jobresult/v2/prod/jobs/{jobId}

Common view templates:
  - CostCenterProcurementSystemView
  - POLineItemSystemView
  - RequisitionLineItemSystemView
  - ReceiptSystemView
  - InvoiceLineItemSystemView
  - PaymentSystemView
  - ContractLineItemSystemView
  - SupplierSystemView

Authentication: OAuth 2.0 Bearer token + apiKey header (handled by client.py)
Pagination: pageToken in response body (pass to next request)
"""

import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

# API path constants — use these with the client methods
SYNC_API = "procurement-reporting-details/v1/prod"
VIEW_META_API = "procurement-reporting-view/v2/prod"
JOB_API = "procurement-reporting-job/v2/prod"
JOB_RESULT_API = "procurement-reporting-jobresult/v2/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register Operational Procurement Reporting tools.

    EXAMPLE TOOL below — use this as a template for the remaining tools.
    See the client.py methods:
      - client.fetch_view(api_path, view_name, filters_dict, page_token)
      - client.fetch_view_count(api_path, view_name, filters_dict)
      - client.submit_job(job_api_path, view_name, filters_dict)
      - client.get_job_status(job_api_path, job_id)
      - client.get_job_results(result_api_path, job_id, page_token)
      - client.fetch_resource(api_path, resource_path, extra_params)
    """

    # ── EXAMPLE TOOL (fully implemented) ──────────────────────────────

    @mcp.tool(
        name="ariba_procurement_query_view",
        description=(
            "Query a procurement reporting view (synchronous). "
            "Common views: POLineItemSystemView, RequisitionLineItemSystemView, "
            "InvoiceLineItemSystemView, ReceiptSystemView, PaymentSystemView. "
            "Use filters like '{\"createdDateFrom\":\"2025-01-01\",\"createdDateTo\":\"2025-01-31\"}'."
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
    # 1. ariba_procurement_list_views
    #    - List all available procurement view templates
    #    - Use: client.fetch_resource(VIEW_META_API, "viewTemplates")
    #
    # 2. ariba_procurement_get_view_metadata
    #    - Get schema for a specific view template
    #    - Use: client.fetch_resource(VIEW_META_API, f"viewTemplates/{view_name}")
    #
    # 3. ariba_procurement_count_view
    #    - Get record count for a view with optional filters
    #    - Use: client.fetch_view_count(SYNC_API, view_name, filters)
    #
    # 4. ariba_procurement_submit_job
    #    - Submit an async job for large datasets
    #    - Use: client.submit_job(JOB_API, view_name, filters)
    #
    # 5. ariba_procurement_get_job_status
    #    - Check status of an async job
    #    - Use: client.get_job_status(JOB_API, job_id)
    #
    # 6. ariba_procurement_get_job_results
    #    - Fetch results of a completed async job
    #    - Use: client.get_job_results(JOB_RESULT_API, job_id, page_token)
    #
    # Copy the example tool pattern above for each new tool.
    # Refer to the Developer Portal for exact request/response schemas.
