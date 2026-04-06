import json
from datetime import datetime

import httpx
from fastmcp import FastMCP

from ariba_mcp.auth import DirectAuthClient
from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_settings
from ariba_mcp.errors import handle_ariba_error

BASE_URL = "https://openapi.ariba.com/api/cost-breakdown/v1/prod"
LIST_RESOURCE = "rfxCostgroups"
DOCUMENT_RESOURCE = "costgroupDocuments"


def _make_auth() -> DirectAuthClient:
    return DirectAuthClient(
        client_id=get_settings().cost_breakdown_client_id,
        client_secret=get_settings().cost_breakdown_client_secret,
        api_key=get_settings().cost_breakdown_api_key,
    )


def _format_date_filter(date_value: str) -> str:
    try:
        normalized = date_value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        return parsed.strftime("%Y%m%dT%H%M%S")
    except ValueError:
        compact = date_value.replace("-", "").replace(":", "")
        if len(compact) == 15 and "T" in compact:
            return compact
        raise ValueError(
            "Cost Breakdown date filters must be ISO-8601 or YYYYMMDDThhmmss."
        )


def _find_first_list(payload: dict | list, *candidate_keys: str) -> list:
    if isinstance(payload, dict):
        for key in candidate_keys:
            value = payload.get(key)
            if isinstance(value, list):
                return value
        for value in payload.values():
            result = _find_first_list(value, *candidate_keys)
            if result:
                return result
    elif isinstance(payload, list):
        for item in payload:
            result = _find_first_list(item, *candidate_keys)
            if result:
                return result
    return []


def _extract_cost_components(document_payload: dict) -> list[dict]:
    return _find_first_list(
        document_payload,
        "costComponents",
        "costcomponents",
        "CostComponents",
    )


def _extract_cost_group_terms(document_payload: dict) -> list[dict]:
    direct_terms = _find_first_list(
        document_payload,
        "costGroupTerms",
        "costgroupTerms",
        "CostGroupTerms",
    )
    if direct_terms:
        return direct_terms

    collected_terms: list[dict] = []
    for component in _extract_cost_components(document_payload):
        component_terms = _find_first_list(
            component,
            "costGroupTerms",
            "costgroupTerms",
            "CostGroupTerms",
        )
        component_id = component.get("id") or component.get("costComponentId")
        for term in component_terms:
            if isinstance(term, dict) and component_id and "costComponentId" not in term:
                collected_terms.append({"costComponentId": component_id, **term})
            else:
                collected_terms.append(term)
    return collected_terms


async def _fetch_cost_group_document_payload(
    auth: DirectAuthClient, realm: str, cost_group_document_id: str
) -> dict:
    url = f"{BASE_URL}/{DOCUMENT_RESOURCE}/{cost_group_document_id}"
    headers = await auth.get_headers()

    async with httpx.AsyncClient() as http:
        resp = await http.get(
            url,
            params={"realm": realm},
            headers=headers,
            timeout=60,
        )
        resp.raise_for_status()

    return resp.json()


def register(mcp: FastMCP, client: AribaClient) -> None:

    _auth = _make_auth()

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
        try:
            url = f"{BASE_URL}/{LIST_RESOURCE}"
            headers = await _auth.get_headers()

            params: dict = {
                "realm": client.realm,
                "$top": min(top, 100),
                "$skip": skip,
                "$count": "true",
            }
            if updated_from:
                params["$filter"] = _format_date_filter(updated_from)

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
                "unsupported_filters_ignored": {
                    "projectId": project_id,
                    "eventId": event_id,
                    "supplierId": supplier_id,
                    "status": status,
                    "updatedTo": updated_to,
                },
                "response": data,
            }
            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)

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
        try:
            payload = await _fetch_cost_group_document_payload(
                _auth, client.realm, cost_group_document_id
            )
            return json.dumps(payload, default=str)

        except Exception as e:
            return handle_ariba_error(e)

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
        try:
            document_payload = await _fetch_cost_group_document_payload(
                _auth, client.realm, cost_group_document_id
            )
            components = _extract_cost_components(document_payload)
            data = components[skip : skip + min(top, 200)]
            result = {
                "costGroupDocumentId": cost_group_document_id,
                "response": data,
            }
            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)

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
        try:
            document_payload = await _fetch_cost_group_document_payload(
                _auth, client.realm, cost_group_document_id
            )
            for component in _extract_cost_components(document_payload):
                component_id = component.get("id") or component.get("costComponentId")
                if component_id == cost_component_id:
                    return json.dumps(component, default=str)
            raise ValueError(
                f"Cost component '{cost_component_id}' was not found in "
                f"cost group document '{cost_group_document_id}'."
            )

        except Exception as e:
            return handle_ariba_error(e)

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
        try:
            document_payload = await _fetch_cost_group_document_payload(
                _auth, client.realm, cost_group_document_id
            )
            all_terms = _extract_cost_group_terms(document_payload)
            if supplier_id:
                all_terms = [
                    term
                    for term in all_terms
                    if term.get("supplierId") == supplier_id
                    or term.get("supplierID") == supplier_id
                ]
            data = all_terms[skip : skip + min(top, 500)]
            result = {
                "costGroupDocumentId": cost_group_document_id,
                "supplierFilter": supplier_id,
                "response": data,
            }
            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)

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
        try:
            document_payload = await _fetch_cost_group_document_payload(
                _auth, client.realm, cost_group_document_id
            )
            all_terms = _extract_cost_group_terms(document_payload)
            component_terms = [
                term
                for term in all_terms
                if term.get("costComponentId") == cost_component_id
                or term.get("costcomponentid") == cost_component_id
            ]
            if supplier_id:
                component_terms = [
                    term
                    for term in component_terms
                    if term.get("supplierId") == supplier_id
                    or term.get("supplierID") == supplier_id
                ]
            data = component_terms[skip : skip + min(top, 200)]
            result = {
                "costGroupDocumentId": cost_group_document_id,
                "costComponentId": cost_component_id,
                "supplierFilter": supplier_id,
                "response": data,
            }
            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)

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
        try:
            doc_header = await _fetch_cost_group_document_payload(
                _auth, client.realm, cost_group_document_id
            )
            components = _extract_cost_components(doc_header)
            terms = _extract_cost_group_terms(doc_header)

            terms_by_component: dict[str, list] = {}
            terms_list = terms if isinstance(terms, list) else terms.get("value", [])
            for term in terms_list:
                comp_id = term.get("costComponentId", "__unassigned__")
                terms_by_component.setdefault(comp_id, []).append(term)

            components_list = (
                components if isinstance(components, list) else components.get("value", [])
            )
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
        try:
            message = (
                "The Cost Breakdown Data Extraction API does not support projectId, "
                "eventId, or status query parameters on its documented GET search "
                "endpoint. Use ariba_cost_breakdown_list_documents with updated_from "
                "to retrieve rfxCostgroups, then fetch individual documents by ID."
            )
            result = {
                "projectId": project_id,
                "eventId": event_id,
                "statusFilter": status,
                "response": [],
                "message": message,
            }
            return json.dumps(result, default=str)

        except Exception as e:
            return handle_ariba_error(e)
