"""Audit Search API.

Owner: Vanshika
Prod URL: https://openapi.ariba.com/api/audit-search/v2/prod
Docs: https://help.sap.com/doc/e42379dea91647fb8fcec25f8fdbddd3/cloud/en-US/index.html

Key endpoints:
  POST /auditRecords/search       — Search audit records with rich filter criteria
  GET  /auditRecords/{recordId}   — Retrieve a specific audit record by ID
  GET  /objectTypes               — List all auditable object types in the realm
  GET  /eventTypes                — List all audit event types available for filtering
  GET  /auditRecords/summary      — Get summary/aggregation counts of audit events

Authentication: OAuth 2.0 Bearer token + apiKey header
Response format: JSON

SAP Ariba Audit Search API allows a client application to:
  - Search the full audit trail for any object (requisition, PO, invoice, user, etc.)
  - Filter by actor (who made the change), object type, event type, and date range
  - Retrieve individual audit records for detailed change inspection
  - List available object types and event types to build dynamic search UIs
  - Get summary counts for compliance dashboards and reporting

Rate limits: Per second: 5 req · Per minute: 100 req · Per hour: 2000 req
Data retention: Audit records are retained per your SAP Ariba configuration (default 2 years)

IMPORTANT: As of October 2023, SAP Ariba migrated to the ICM-based Audit Service.
All new audit data flows through this API. Legacy audit log exports are deprecated.
"""

import json
import os
from datetime import datetime, timezone

import httpx
from fastmcp import FastMCP

from ariba_mcp.auth import DirectAuthClient
from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://openapi.ariba.com/api/audit-search/v2/prod"


def _make_auth() -> DirectAuthClient:
    return DirectAuthClient(
        client_id=os.getenv("AUDIT_SEARCH_CLIENT_ID", ""),
        client_secret=os.getenv("AUDIT_SEARCH_CLIENT_SECRET", ""),
        api_key=os.getenv("AUDIT_SEARCH_API_KEY", ""),
    )

# Common auditable object types (non-exhaustive — use ariba_audit_list_object_types for full list)
COMMON_OBJECT_TYPES = [
    "Requisition",
    "PurchaseOrder",
    "Invoice",
    "Contract",
    "SupplierProfile",
    "User",
    "SourcingProject",
    "SourcingEvent",
    "ContractWorkspace",
    "ApprovalsFlow",
]

# Common event types
COMMON_EVENT_TYPES = [
    "Create",
    "Update",
    "Delete",
    "Submit",
    "Approve",
    "Deny",
    "Withdraw",
    "Login",
    "Logout",
    "Export",
    "StatusChange",
]


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register all Audit Search API tools with the MCP server."""

    _auth = _make_auth()

    # ------------------------------------------------------------------
    # 1. Search Audit Records (core search endpoint)
    # ------------------------------------------------------------------
    @mcp.tool(
        name="ariba_audit_search",
        description=(
            "Search the SAP Ariba audit trail for activity records matching your criteria. "
            "Returns who made what change, on which object, and when. "
            "FILTERS (all optional, combine freely):\n"
            "  - from_date / to_date: ISO-8601 datetime range, e.g. '2024-01-01T00:00:00Z'\n"
            "  - actor_id: SAP Ariba username who performed the action (e.g. 'jsmith@company.com')\n"
            "  - object_type: type of object audited — "
            "Requisition | PurchaseOrder | Invoice | Contract | User | SourcingProject | etc.\n"
            "  - object_id: specific document or record ID to audit (e.g. 'PR-12345')\n"
            "  - event_type: type of action — Create | Update | Delete | Submit | Approve | Deny | Login | etc.\n"
            "  - top: max records to return (default 50, max 200)\n"
            "  - skip: offset for pagination\n"
            "At least one filter is recommended — querying without any filters may time out on large realms."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def search_audit_records(
        from_date: str | None = None,
        to_date: str | None = None,
        actor_id: str | None = None,
        object_type: str | None = None,
        object_id: str | None = None,
        event_type: str | None = None,
        top: int = 50,
        skip: int = 0,
    ) -> str:
        """
        POST /auditRecords/search
        Searches audit records. Accepts a JSON body with filter criteria.
        All filter fields are optional but at least one is recommended.
        """
        try:
            url = f"{BASE_URL}/auditRecords/search"
            headers = await _auth.get_headers()
            headers["Content-Type"] = "application/json"

            # Build filter body — only include fields that were provided
            filters: dict = {}
            if from_date:
                filters["fromDate"] = from_date
            if to_date:
                filters["toDate"] = to_date
            if actor_id:
                filters["actorId"] = actor_id
            if object_type:
                filters["objectType"] = object_type
            if object_id:
                filters["objectId"] = object_id
            if event_type:
                filters["eventType"] = event_type

            payload: dict = {
                "filters": filters,
                "$top": min(top, 200),   # cap at API max
                "$skip": skip,
            }

            params = {"realm": client.realm}

            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    url,
                    params=params,
                    headers=headers,
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()

            data = resp.json()

            # Annotate with query metadata for easier consumption
            result = {
                "query": {
                    "filters": filters,
                    "top": top,
                    "skip": skip,
                },
                "response": data,
            }
            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)

    # ------------------------------------------------------------------
    # 2. Get Audit Record by ID
    # ------------------------------------------------------------------
    @mcp.tool(
        name="ariba_audit_get_record",
        description=(
            "Retrieve a single audit record by its unique recordId. "
            "Returns the full detail of one audit event including: actor, timestamp, "
            "object type, object ID, event type, before/after field values (delta), "
            "and IP address. "
            "Use ariba_audit_search first to find a recordId, then call this for full details."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_audit_record(record_id: str) -> str:
        """
        GET /auditRecords/{recordId}
        Returns full details for a single audit record.
        """
        try:
            url = f"{BASE_URL}/auditRecords/{record_id}"
            headers = await _auth.get_headers()

            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    url,
                    params={"realm": client.realm},
                    headers=headers,
                    timeout=60,
                )
                resp.raise_for_status()

            return json.dumps(resp.json(), default=str)

        except Exception as e:
            return handle_ariba_error(e)

    # ------------------------------------------------------------------
    # 3. List Object Types
    # ------------------------------------------------------------------
    @mcp.tool(
        name="ariba_audit_list_object_types",
        description=(
            "List all auditable object types available in the realm. "
            "Use this to discover valid objectType values for ariba_audit_search. "
            "Examples: Requisition, PurchaseOrder, Invoice, Contract, User, SourcingProject, etc. "
            "The full list is realm-specific and may include custom object types."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def list_object_types() -> str:
        """
        GET /objectTypes
        Returns all auditable object types for the realm.
        """
        try:
            url = f"{BASE_URL}/objectTypes"
            headers = await _auth.get_headers()

            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    url,
                    params={"realm": client.realm},
                    headers=headers,
                    timeout=60,
                )
                resp.raise_for_status()

            return json.dumps(resp.json(), default=str)

        except Exception as e:
            return handle_ariba_error(e)

    # ------------------------------------------------------------------
    # 4. List Event Types
    # ------------------------------------------------------------------
    @mcp.tool(
        name="ariba_audit_list_event_types",
        description=(
            "List all audit event types available for filtering in this realm. "
            "Use this to discover valid eventType values for ariba_audit_search. "
            "Examples: Create, Update, Delete, Submit, Approve, Deny, Login, Logout, Export, StatusChange. "
            "The list may vary by realm configuration and enabled modules."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def list_event_types() -> str:
        """
        GET /eventTypes
        Returns all audit event types the realm supports.
        """
        try:
            url = f"{BASE_URL}/eventTypes"
            headers = await _auth.get_headers()

            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    url,
                    params={"realm": client.realm},
                    headers=headers,
                    timeout=60,
                )
                resp.raise_for_status()

            return json.dumps(resp.json(), default=str)

        except Exception as e:
            return handle_ariba_error(e)

    # ------------------------------------------------------------------
    # 5. Get Audit Summary (aggregation counts)
    # ------------------------------------------------------------------
    @mcp.tool(
        name="ariba_audit_get_summary",
        description=(
            "Get a summary count of audit events grouped by object type and event type "
            "for a given time window. Useful for compliance dashboards and anomaly detection. "
            "Pass from_date and to_date in ISO-8601 format (e.g. '2024-01-01T00:00:00Z'). "
            "Optionally filter by object_type or actor_id to narrow the summary."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def get_audit_summary(
        from_date: str | None = None,
        to_date: str | None = None,
        object_type: str | None = None,
        actor_id: str | None = None,
    ) -> str:
        """
        GET /auditRecords/summary
        Returns aggregated counts of audit events, grouped by objectType and eventType.
        """
        try:
            url = f"{BASE_URL}/auditRecords/summary"
            headers = await _auth.get_headers()

            params: dict = {"realm": client.realm}
            if from_date:
                params["fromDate"] = from_date
            if to_date:
                params["toDate"] = to_date
            if object_type:
                params["objectType"] = object_type
            if actor_id:
                params["actorId"] = actor_id

            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=60,
                )
                resp.raise_for_status()

            return json.dumps(resp.json(), default=str)

        except Exception as e:
            return handle_ariba_error(e)

    # ------------------------------------------------------------------
    # 6. Search by Actor (convenience tool — who did what)
    # ------------------------------------------------------------------
    @mcp.tool(
        name="ariba_audit_search_by_actor",
        description=(
            "Find all audit events performed by a specific user (actor). "
            "Pass the user's SAP Ariba username / email as actor_id. "
            "Optionally narrow by date range, object type, or event type. "
            "Useful for investigating what a specific user did during an incident window. "
            "Returns the same audit records as ariba_audit_search but pre-filtered by actor."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def search_by_actor(
        actor_id: str,
        from_date: str | None = None,
        to_date: str | None = None,
        object_type: str | None = None,
        event_type: str | None = None,
        top: int = 50,
    ) -> str:
        """
        POST /auditRecords/search  (pre-filtered by actorId)
        Convenience wrapper — actor_id is mandatory here.
        """
        try:
            url = f"{BASE_URL}/auditRecords/search"
            headers = await _auth.get_headers()
            headers["Content-Type"] = "application/json"

            filters: dict = {"actorId": actor_id}
            if from_date:
                filters["fromDate"] = from_date
            if to_date:
                filters["toDate"] = to_date
            if object_type:
                filters["objectType"] = object_type
            if event_type:
                filters["eventType"] = event_type

            payload = {
                "filters": filters,
                "$top": min(top, 200),
                "$skip": 0,
            }

            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    url,
                    params={"realm": client.realm},
                    headers=headers,
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()

            result = {
                "actor": actor_id,
                "filters": filters,
                "response": resp.json(),
            }
            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)

    # ------------------------------------------------------------------
    # 7. Search by Object (convenience tool — full history of one document)
    # ------------------------------------------------------------------
    @mcp.tool(
        name="ariba_audit_search_by_object",
        description=(
            "Get the complete audit trail for a specific document or object. "
            "Pass the object_type (e.g. 'Requisition', 'PurchaseOrder', 'Invoice') "
            "and the object_id (the document's unique ID, e.g. 'PR-12345', 'PO-78900'). "
            "Returns every event ever recorded for that object: who created it, "
            "who modified it, what changed, who approved it, and when each action happened. "
            "Optionally filter by event_type or date range."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def search_by_object(
        object_type: str,
        object_id: str,
        from_date: str | None = None,
        to_date: str | None = None,
        event_type: str | None = None,
        top: int = 100,
    ) -> str:
        """
        POST /auditRecords/search  (pre-filtered by objectType + objectId)
        Returns the complete change history for one specific document.
        """
        try:
            url = f"{BASE_URL}/auditRecords/search"
            headers = await _auth.get_headers()
            headers["Content-Type"] = "application/json"

            filters: dict = {
                "objectType": object_type,
                "objectId": object_id,
            }
            if from_date:
                filters["fromDate"] = from_date
            if to_date:
                filters["toDate"] = to_date
            if event_type:
                filters["eventType"] = event_type

            payload = {
                "filters": filters,
                "$top": min(top, 200),
                "$skip": 0,
            }

            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    url,
                    params={"realm": client.realm},
                    headers=headers,
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()

            result = {
                "object": {"type": object_type, "id": object_id},
                "filters": filters,
                "response": resp.json(),
            }
            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)

    # ------------------------------------------------------------------
    # 8. Search Recent Audit Records (last N hours — quick compliance check)
    # ------------------------------------------------------------------
    @mcp.tool(
        name="ariba_audit_search_recent",
        description=(
            "Fetch the most recent audit events from the last N hours (default: 24). "
            "A quick way to see what happened today / recently without specifying exact timestamps. "
            "Optionally filter by object_type, event_type, or actor_id. "
            "Returns records sorted by most recent first."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def search_recent(
        hours_back: int = 24,
        object_type: str | None = None,
        event_type: str | None = None,
        actor_id: str | None = None,
        top: int = 50,
    ) -> str:
        """
        POST /auditRecords/search  (pre-filtered to the last N hours)
        Convenience wrapper — auto-computes fromDate / toDate from hours_back.
        """
        try:
            from datetime import timedelta

            now = datetime.now(timezone.utc)
            from_dt = now - timedelta(hours=hours_back)

            from_date_str = from_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            to_date_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")

            url = f"{BASE_URL}/auditRecords/search"
            headers = await _auth.get_headers()
            headers["Content-Type"] = "application/json"

            filters: dict = {
                "fromDate": from_date_str,
                "toDate": to_date_str,
            }
            if object_type:
                filters["objectType"] = object_type
            if event_type:
                filters["eventType"] = event_type
            if actor_id:
                filters["actorId"] = actor_id

            payload = {
                "filters": filters,
                "$top": min(top, 200),
                "$skip": 0,
            }

            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    url,
                    params={"realm": client.realm},
                    headers=headers,
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()

            result = {
                "window": {
                    "hours_back": hours_back,
                    "from": from_date_str,
                    "to": to_date_str,
                },
                "filters": filters,
                "response": resp.json(),
            }
            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)