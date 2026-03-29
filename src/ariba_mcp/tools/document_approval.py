"""Document Approval and Audit APIs for SAP Ariba.

Covers:
- Document Approval API:         document-approval/v1/prod
- Audit Search API:              audit-search/v1/prod
- Transaction Monitoring API:    transaction-monitoring/v1/prod

Docs: https://help.sap.com/docs/ariba-apis
"""

import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

APPROVAL_API = "document-approval/v1/prod"
AUDIT_API = "audit-search/v1/prod"
MONITORING_API = "transaction-monitoring/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register Document Approval and Audit tools."""

    @mcp.tool(
        name="ariba_approval_list_pending",
        description="List pending document approvals. Returns documents awaiting approval action.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_pending(page_token: str | None = None) -> str:
        try:
            params = {}
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(APPROVAL_API, "pendingApprovals", params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_approval_get_document",
        description="Get approval details for a specific document by its approvable ID.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_document(approvable_id: str) -> str:
        try:
            result = await client.fetch_resource(APPROVAL_API, f"approvables/{approvable_id}")
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_audit_search",
        description=(
            "Search audit logs. Query audit records for compliance and governance. "
            "Filters can include date ranges, document types, and user actions."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def search_audit(
        filters: str | None = None,
        page_token: str | None = None,
    ) -> str:
        try:
            params: dict = {}
            if filters:
                params["filters"] = filters
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(AUDIT_API, "auditRecords", params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_transaction_monitor",
        description="Monitor transaction activity. Returns transaction status and integration events.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def monitor_transactions(
        filters: str | None = None,
        page_token: str | None = None,
    ) -> str:
        try:
            params: dict = {}
            if filters:
                params["filters"] = filters
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(MONITORING_API, "transactions", params)
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)
