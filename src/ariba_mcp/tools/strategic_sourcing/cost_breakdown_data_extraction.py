"""Cost Breakdown Data Extraction API.

Owner: Vanshika
Prod URL: https://openapi.ariba.com/api/cost-breakdown/v1/prod
Docs: https://help.sap.com/doc/525b79f5d831496abfcd2bddd46626ad/cloud/en-US/index.html

Summary:
    For customer developers who develop a client application to search for cost group
    documents and to download cost components and the associated cost group terms from
    a cost group document.

    Cost breakdown data is used in SAP Ariba Product Sourcing during sourcing events
    to capture detailed manufacturing/supplier cost structures. A cost group document
    contains:
      - Cost Components  : individual cost line items (material, labour, overhead, etc.)
      - Cost Group Terms : supplier responses per cost component (price, quantity, UOM)

    This is a READ-ONLY extraction API — no create/update/delete operations.

Domain context:
    Cost breakdown is configured under SAP Ariba Strategic Sourcing / Product Sourcing.
    A sourcing project contains one or more sourcing events. Each event can have one or
    more cost group documents attached. Each cost group document holds cost components
    and the associated cost group terms (supplier bid data per component).

Endpoints covered:
  ── Cost Group Document Search ─────────────────────────────────────────────
  GET  /costGroupDocuments                             Search cost group documents
  GET  /costGroupDocuments/{costGroupDocumentId}       Get a specific cost group document

  ── Cost Components (line items within a cost group document) ───────────────
  GET  /costGroupDocuments/{costGroupDocumentId}/costComponents
                                                       Get cost components of a document
  GET  /costGroupDocuments/{costGroupDocumentId}/costComponents/{costComponentId}
                                                       Get a single cost component

  ── Cost Group Terms (supplier bid data per cost component) ─────────────────
  GET  /costGroupDocuments/{costGroupDocumentId}/costGroupTerms
                                                       Get all cost group terms of a document
  GET  /costGroupDocuments/{costGroupDocumentId}/costComponents/{costComponentId}/costGroupTerms
                                                       Get terms for a specific cost component

Authentication: OAuth 2.0 Bearer token + apiKey header
Response format: JSON

Key workflow:
    1. GET /costGroupDocuments             → search and find costGroupDocumentId
       (filter by projectId, eventId, supplierId, status, or updatedDate range)
    2. GET /costGroupDocuments/{id}        → verify document details
    3. GET /costGroupDocuments/{id}/costComponents
                                           → download all cost line items
    4. GET /costGroupDocuments/{id}/costGroupTerms
                                           → download all supplier bid data
    OR
    3. GET /costGroupDocuments/{id}/costComponents/{componentId}/costGroupTerms
                                           → targeted extraction: one component's terms

Data model:
    CostGroupDocument
        ├── id, title, status, projectId, eventId, supplierId, version, updatedDate
        └── CostComponents[]
                ├── id, name, description, componentType, sequence
                └── CostGroupTerms[]
                        ├── id, supplierId, price, quantity, unitOfMeasure, currency
                        └── adjustmentFactor, comments, isAlternative

Cost component types (componentType):
    Material | Labour | Overhead | Tooling | Logistics | Custom

Cost group document statuses:
    Draft | Submitted | Accepted | Rejected | Revised
"""

import json

import httpx
from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_PATH = "cost-breakdown/v1/prod"


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register all Cost Breakdown Data Extraction API tools with the MCP server."""

    # ======================================================================
    # 1. Search Cost Group Documents
    # ======================================================================

    @mcp.tool(
        name="ariba_cost_breakdown_list_documents",
        description=(
            "Search for cost group documents in SAP Ariba Product Sourcing. "
            "A cost group document holds detailed cost breakdown data (material, labour, "
            "overhead, tooling, logistics) attached to a sourcing event. "
            "\n\nFilter options (all optional — combine freely):"
            "\n  - project_id     : sourcing project ID (e.g. 'WS1234567')"
            "\n  - event_id       : sourcing event ID (e.g. 'Doc1234567')"
            "\n  - supplier_id    : filter by supplier system ID"
            "\n  - status         : Draft | Submitted | Accepted | Rejected | Revised"
            "\n  - updated_from   : ISO-8601 datetime lower bound (e.g. '2024-01-01T00:00:00Z')"
            "\n  - updated_to     : ISO-8601 datetime upper bound"
            "\n  - top / skip     : pagination (default top=20, max 100)"
            "\nReturns costGroupDocumentId needed for subsequent cost component/term extraction."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def list_cost_group_documents(
        project_id: str | None = None,
        event_id: str | None = None,
        supplier_id: str | None = None,
        status: str | None = None,
        updated_from: str | None = None,
        updated_to: str | None = None,
        top: int = 20,
        skip: int = 0,
    ) -> str:
        """
        GET /costGroupDocuments
        Returns cost group documents matching the given filters.
        """
        try:
            url = f"{client.base_url}/{API_PATH}/costGroupDocuments"
            headers = await client.auth.get_headers()

            # Build OData $filter parts
            filter_parts: list[str] = []
            if project_id:
                filter_parts.append(f"projectId eq '{project_id}'")
            if event_id:
                filter_parts.append(f"eventId eq '{event_id}'")
            if supplier_id:
                filter_parts.append(f"supplierId eq '{supplier_id}'")
            if status:
                filter_parts.append(f"status eq '{status}'")
            if updated_from:
                filter_parts.append(f"updatedDate ge '{updated_from}'")
            if updated_to:
                filter_parts.append(f"updatedDate le '{updated_to}'")

            params: dict = {
                "realm": client.realm,
                "$top": min(top, 100),
                "$skip": skip,
            }
            if filter_parts:
                params["$filter"] = " and ".join(filter_parts)

            async with httpx.AsyncClient() as http:
                resp = await http.get(url, params=params, headers=headers, timeout=60)
                resp.raise_for_status()

            data = resp.json()
            result = {
                "filters_applied": {
                    "projectId": project_id,
                    "eventId": event_id,
                    "supplierId": supplier_id,
                    "status": status,
                    "updatedFrom": updated_from,
                    "updatedTo": updated_to,
                },
                "response": data,
            }
            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)

    # ======================================================================
    # 2. Get Single Cost Group Document
    # ======================================================================

    @mcp.tool(
        name="ariba_cost_breakdown_get_document",
        description=(
            "Get full header details of a specific cost group document by its ID. "
            "Returns: costGroupDocumentId, title, status, version, projectId, eventId, "
            "supplierId, createdDate, updatedDate, currency, and total cost summary. "
            "Use ariba_cost_breakdown_list_documents first to find the costGroupDocumentId."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_cost_group_document(cost_group_document_id: str) -> str:
        """
        GET /costGroupDocuments/{costGroupDocumentId}
        Returns header-level details for one cost group document.
        """
        try:
            url = f"{client.base_url}/{API_PATH}/costGroupDocuments/{cost_group_document_id}"
            headers = await client.auth.get_headers()

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

    # ======================================================================
    # 3. Get All Cost Components of a Document
    # ======================================================================

    @mcp.tool(
        name="ariba_cost_breakdown_get_components",
        description=(
            "Download all cost components from a cost group document. "
            "Cost components are the individual line items in a cost breakdown structure — "
            "e.g. Raw Material, Direct Labour, Manufacturing Overhead, Tooling, Logistics, Profit. "
            "Returns for each component: costComponentId, name, description, componentType, "
            "sequence number, and unit of measure. "
            "Use the costComponentId values to then fetch cost group terms per component. "
            "Pass the costGroupDocumentId from ariba_cost_breakdown_list_documents."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_cost_components(
        cost_group_document_id: str,
        top: int = 100,
        skip: int = 0,
    ) -> str:
        """
        GET /costGroupDocuments/{costGroupDocumentId}/costComponents
        Returns all cost components for the specified cost group document.
        """
        try:
            url = (
                f"{client.base_url}/{API_PATH}"
                f"/costGroupDocuments/{cost_group_document_id}/costComponents"
            )
            headers = await client.auth.get_headers()

            params: dict = {
                "realm": client.realm,
                "$top": min(top, 200),
                "$skip": skip,
            }

            async with httpx.AsyncClient() as http:
                resp = await http.get(url, params=params, headers=headers, timeout=60)
                resp.raise_for_status()

            data = resp.json()
            result = {
                "costGroupDocumentId": cost_group_document_id,
                "response": data,
            }
            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)

    # ======================================================================
    # 4. Get Single Cost Component
    # ======================================================================

    @mcp.tool(
        name="ariba_cost_breakdown_get_component",
        description=(
            "Get the full details of a single cost component by its ID. "
            "Returns: costComponentId, name, description, componentType "
            "(Material | Labour | Overhead | Tooling | Logistics | Custom), "
            "sequence, unitOfMeasure, and any custom attributes. "
            "Requires both costGroupDocumentId and costComponentId. "
            "Use ariba_cost_breakdown_get_components to find valid costComponentId values."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_cost_component(
        cost_group_document_id: str,
        cost_component_id: str,
    ) -> str:
        """
        GET /costGroupDocuments/{costGroupDocumentId}/costComponents/{costComponentId}
        Returns details for a single cost component.
        """
        try:
            url = (
                f"{client.base_url}/{API_PATH}"
                f"/costGroupDocuments/{cost_group_document_id}"
                f"/costComponents/{cost_component_id}"
            )
            headers = await client.auth.get_headers()

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

    # ======================================================================
    # 5. Get All Cost Group Terms of a Document
    # ======================================================================

    @mcp.tool(
        name="ariba_cost_breakdown_get_all_terms",
        description=(
            "Download ALL cost group terms from a cost group document in one call. "
            "Cost group terms are the supplier bid responses per cost component — "
            "they contain the actual price, quantity, unit of measure, currency, "
            "adjustment factor, and supplier comments for each cost line. "
            "This is the main data extraction endpoint — use it for bulk extraction "
            "of all supplier cost data for a document. "
            "Returns terms grouped by costComponentId with supplierId, price, quantity, "
            "UOM, currency, adjustmentFactor, isAlternative flag, and comments. "
            "Pass costGroupDocumentId from ariba_cost_breakdown_list_documents."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_all_cost_group_terms(
        cost_group_document_id: str,
        supplier_id: str | None = None,
        top: int = 200,
        skip: int = 0,
    ) -> str:
        """
        GET /costGroupDocuments/{costGroupDocumentId}/costGroupTerms
        Returns all supplier cost group terms for the entire cost group document.
        Optionally filtered by supplierId.
        """
        try:
            url = (
                f"{client.base_url}/{API_PATH}"
                f"/costGroupDocuments/{cost_group_document_id}/costGroupTerms"
            )
            headers = await client.auth.get_headers()

            params: dict = {
                "realm": client.realm,
                "$top": min(top, 500),
                "$skip": skip,
            }
            if supplier_id:
                params["$filter"] = f"supplierId eq '{supplier_id}'"

            async with httpx.AsyncClient() as http:
                resp = await http.get(url, params=params, headers=headers, timeout=60)
                resp.raise_for_status()

            data = resp.json()
            result = {
                "costGroupDocumentId": cost_group_document_id,
                "supplierFilter": supplier_id,
                "response": data,
            }
            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)

    # ======================================================================
    # 6. Get Cost Group Terms for a Specific Component
    # ======================================================================

    @mcp.tool(
        name="ariba_cost_breakdown_get_component_terms",
        description=(
            "Get cost group terms for one specific cost component within a document. "
            "Use this for targeted extraction — when you need supplier bid data "
            "for just one line item (e.g. only the 'Raw Material' component). "
            "Returns: supplierId, price, quantity, unitOfMeasure, currency, "
            "adjustmentFactor, isAlternative, and supplier comments. "
            "Requires costGroupDocumentId + costComponentId. "
            "To get all terms across all components at once, use ariba_cost_breakdown_get_all_terms."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_component_cost_group_terms(
        cost_group_document_id: str,
        cost_component_id: str,
        supplier_id: str | None = None,
        top: int = 100,
        skip: int = 0,
    ) -> str:
        """
        GET /costGroupDocuments/{costGroupDocumentId}/costComponents/{costComponentId}/costGroupTerms
        Returns cost group terms for a single cost component.
        """
        try:
            url = (
                f"{client.base_url}/{API_PATH}"
                f"/costGroupDocuments/{cost_group_document_id}"
                f"/costComponents/{cost_component_id}/costGroupTerms"
            )
            headers = await client.auth.get_headers()

            params: dict = {
                "realm": client.realm,
                "$top": min(top, 200),
                "$skip": skip,
            }
            if supplier_id:
                params["$filter"] = f"supplierId eq '{supplier_id}'"

            async with httpx.AsyncClient() as http:
                resp = await http.get(url, params=params, headers=headers, timeout=60)
                resp.raise_for_status()

            data = resp.json()
            result = {
                "costGroupDocumentId": cost_group_document_id,
                "costComponentId": cost_component_id,
                "supplierFilter": supplier_id,
                "response": data,
            }
            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)

    # ======================================================================
    # 7. Full Document Extraction (convenience — all data in one call)
    # ======================================================================

    @mcp.tool(
        name="ariba_cost_breakdown_extract_full_document",
        description=(
            "Extract the complete cost breakdown data for a document in one operation: "
            "document header + all cost components + all cost group terms. "
            "This is a convenience tool that makes 3 sequential API calls and returns "
            "a unified JSON object with the full cost structure. "
            "Use this for reporting, analysis, or exporting a complete cost breakdown. "
            "For very large documents (100+ components), use the individual tools instead "
            "to avoid timeout. "
            "Pass the costGroupDocumentId from ariba_cost_breakdown_list_documents."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def extract_full_document(cost_group_document_id: str) -> str:
        """
        Composite call:
          1. GET /costGroupDocuments/{id}                → header
          2. GET /costGroupDocuments/{id}/costComponents → components
          3. GET /costGroupDocuments/{id}/costGroupTerms → all supplier terms
        Assembles into one unified dict for easy consumption.
        """
        try:
            base_doc_url = f"{client.base_url}/{API_PATH}/costGroupDocuments/{cost_group_document_id}"
            headers = await client.auth.get_headers()
            realm_params = {"realm": client.realm}

            async with httpx.AsyncClient() as http:
                # 1. Header
                r1 = await http.get(base_doc_url, params=realm_params, headers=headers, timeout=60)
                r1.raise_for_status()
                doc_header = r1.json()

                # 2. Cost Components
                r2 = await http.get(
                    f"{base_doc_url}/costComponents",
                    params={**realm_params, "$top": 500},
                    headers=headers,
                    timeout=60,
                )
                r2.raise_for_status()
                components = r2.json()

                # 3. All Cost Group Terms
                r3 = await http.get(
                    f"{base_doc_url}/costGroupTerms",
                    params={**realm_params, "$top": 500},
                    headers=headers,
                    timeout=60,
                )
                r3.raise_for_status()
                terms = r3.json()

            # Build a unified nested structure:
            # costGroupDocument
            #   header: { ... }
            #   costComponents: [ { ...component, terms: [...] } ]
            terms_by_component: dict[str, list] = {}
            terms_list = terms if isinstance(terms, list) else terms.get("value", [])
            for term in terms_list:
                comp_id = term.get("costComponentId", "__unassigned__")
                terms_by_component.setdefault(comp_id, []).append(term)

            components_list = components if isinstance(components, list) else components.get("value", [])
            enriched_components = []
            for comp in components_list:
                comp_id = comp.get("id") or comp.get("costComponentId", "")
                enriched_components.append({
                    **comp,
                    "costGroupTerms": terms_by_component.get(comp_id, []),
                })

            result = {
                "costGroupDocumentId": cost_group_document_id,
                "header": doc_header,
                "costComponents": enriched_components,
                "summary": {
                    "totalComponents": len(components_list),
                    "totalTerms": len(terms_list),
                },
            }
            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)

    # ======================================================================
    # 8. Search by Project — list all documents for a project
    # ======================================================================

    @mcp.tool(
        name="ariba_cost_breakdown_search_by_project",
        description=(
            "Find all cost group documents associated with a specific sourcing project. "
            "Convenience wrapper around the document search — projectId is required. "
            "Returns all cost group documents attached to events within that project, "
            "including status, supplierId, version, and updatedDate for each. "
            "Optionally filter by event_id or status."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def search_by_project(
        project_id: str,
        event_id: str | None = None,
        status: str | None = None,
        top: int = 50,
    ) -> str:
        """
        GET /costGroupDocuments  (pre-filtered by projectId)
        Returns all cost group documents for the given sourcing project.
        """
        try:
            url = f"{client.base_url}/{API_PATH}/costGroupDocuments"
            headers = await client.auth.get_headers()

            filter_parts = [f"projectId eq '{project_id}'"]
            if event_id:
                filter_parts.append(f"eventId eq '{event_id}'")
            if status:
                filter_parts.append(f"status eq '{status}'")

            params: dict = {
                "realm": client.realm,
                "$filter": " and ".join(filter_parts),
                "$top": min(top, 100),
                "$skip": 0,
            }

            async with httpx.AsyncClient() as http:
                resp = await http.get(url, params=params, headers=headers, timeout=60)
                resp.raise_for_status()

            data = resp.json()
            result = {
                "projectId": project_id,
                "eventId": event_id,
                "statusFilter": status,
                "response": data,
            }
            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)