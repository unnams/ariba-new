import csv
import io
import json

import httpx
from fastmcp import FastMCP

from ariba_mcp.auth import DirectAuthClient
from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_settings
from ariba_mcp.errors import handle_ariba_error

API_PATH = "supplierdatapagination/v4/prod"


def _make_sdp_auth() -> DirectAuthClient:
    s = get_settings()
    return DirectAuthClient(
        client_id=s.ariba_sdp_client_id,
        client_secret=s.ariba_sdp_client_secret,
        api_key=s.ariba_sdp_api_key,
    )


def _csv_to_json(csv_text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(csv_text))
    return [row for row in reader]


def register(mcp: FastMCP, client: AribaClient) -> None:

    _sdp_auth = _make_sdp_auth()

    @mcp.tool(
        name="ariba_supplier_list_all",
        description=(
            "List suppliers/vendors from the realm with optional client-side pagination. "
            "Returns supplier name, SM vendor ID, ERP vendor ID, AN ID, "
            "registration status, qualification status, address, and more. "
            "Use page and page_size to paginate through results (e.g. page=1 page_size=50 "
            "returns rows 1-50, page=2 returns rows 51-100). "
            "Omit page/page_size to get all records at once."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_all_suppliers(page: int | None = None, page_size: int = 50) -> str:
        try:
            url = f"{client.base_url}/{API_PATH}/vendorDataRequests"
            headers = await _sdp_auth.get_headers()
            headers["Content-Type"] = "application/json"
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    url,
                    params={"realm": client.realm},
                    headers=headers,
                    json={},
                    timeout=60,
                )
                resp.raise_for_status()

            rows = _csv_to_json(resp.text)

            if page is not None:
                start = (page - 1) * page_size
                end = start + page_size
                page_rows = rows[start:end]
                result = {
                    "page": page,
                    "page_size": page_size,
                    "total_count": len(rows),
                    "total_pages": -(-len(rows) // page_size),
                    "returned_count": len(page_rows),
                    "suppliers": page_rows,
                }
            else:
                result = {
                    "total_count": len(rows),
                    "suppliers": rows,
                }
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_supplier_get_by_vendor_id",
        description=(
            "Get supplier data for specific vendor IDs. "
            "Pass one or more SM Vendor IDs (comma-separated, e.g. 'S70530768,S78201759'). "
            "Returns detailed supplier information."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_by_vendor_id(vendor_ids: str) -> str:
        try:
            ids = [v.strip() for v in vendor_ids.split(",")]
            url = f"{client.base_url}/{API_PATH}/vendorDataRequests"
            headers = await _sdp_auth.get_headers()
            headers["Content-Type"] = "application/json"
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    url,
                    params={"realm": client.realm},
                    headers=headers,
                    json={"smVendorIds": ids},
                    timeout=60,
                )
                resp.raise_for_status()

            rows = _csv_to_json(resp.text)
            result = {
                "total_count": len(rows),
                "suppliers": rows,
            }
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_supplier_search",
        description=(
            "Search suppliers by name. Fetches all suppliers and filters by name substring. "
            "Case-insensitive search."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def search_suppliers(name: str) -> str:
        try:
            url = f"{client.base_url}/{API_PATH}/vendorDataRequests"
            headers = await _sdp_auth.get_headers()
            headers["Content-Type"] = "application/json"
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    url,
                    params={"realm": client.realm},
                    headers=headers,
                    json={},
                    timeout=60,
                )
                resp.raise_for_status()

            rows = _csv_to_json(resp.text)
            name_lower = name.lower()
            matched = [r for r in rows if name_lower in r.get("Supplier Name", "").lower()]
            result = {
                "query": name,
                "total_count": len(matched),
                "suppliers": matched,
            }
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_supplier_filter_by_status",
        description=(
            "Filter suppliers by registration or qualification status. "
            "Registration statuses: Registered, Invited, NotInvited, RegistrationDenied. "
            "Qualification statuses: Qualified, QualifiedForSome, NotQualified, Unknown."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def filter_by_status(
        registration_status: str | None = None,
        qualification_status: str | None = None,
    ) -> str:
        try:
            url = f"{client.base_url}/{API_PATH}/vendorDataRequests"
            headers = await _sdp_auth.get_headers()
            headers["Content-Type"] = "application/json"
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    url,
                    params={"realm": client.realm},
                    headers=headers,
                    json={},
                    timeout=60,
                )
                resp.raise_for_status()

            rows = _csv_to_json(resp.text)
            filtered = rows
            if registration_status:
                filtered = [r for r in filtered if r.get("Registration Status") == registration_status]
            if qualification_status:
                filtered = [r for r in filtered if r.get("Qualification Status") == qualification_status]
            result = {
                "filters": {"registration_status": registration_status, "qualification_status": qualification_status},
                "total_count": len(filtered),
                "suppliers": filtered,
            }
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_supplier_summary",
        description=(
            "Get a summary of all suppliers: total count, "
            "breakdown by registration status and qualification status."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def supplier_summary() -> str:
        try:
            url = f"{client.base_url}/{API_PATH}/vendorDataRequests"
            headers = await _sdp_auth.get_headers()
            headers["Content-Type"] = "application/json"
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    url,
                    params={"realm": client.realm},
                    headers=headers,
                    json={},
                    timeout=60,
                )
                resp.raise_for_status()

            rows = _csv_to_json(resp.text)

            unique = {}
            for r in rows:
                vid = r.get("SM Vendor ID", "")
                if vid and vid not in unique:
                    unique[vid] = r

            by_reg: dict[str, int] = {}
            by_qual: dict[str, int] = {}
            for r in unique.values():
                reg = r.get("Registration Status", "Unknown")
                qual = r.get("Qualification Status", "Unknown")
                by_reg[reg] = by_reg.get(reg, 0) + 1
                by_qual[qual] = by_qual.get(qual, 0) + 1

            result = {
                "total_unique_suppliers": len(unique),
                "total_rows": len(rows),
                "by_registration_status": by_reg,
                "by_qualification_status": by_qual,
            }
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)
    @mcp.tool(
        name="ariba_vendor_qna_bankdetails"
        description=
          "Fetch supplier workspace questionnaire Q&A data from SAP Ariba "
          "Supplier Data Pagination API for a given supplier/vendor ID."
          ),
          annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
      )
      async def supplier_qna(vendor_id:str,) -> str:
      try:
             url = f"{client.base_url}/{API_PATH}/vendors/{vendor_id}/workspaces/questionnaires/qna"
             headers = await _sdp_auth.get_headers()
             headers["Content-Type"] = "application/json"
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    url,
                    params={"realm": client.realm},
                    headers=headers,
                    json={},
                    timeout=60,
                )
                resp.raise_for_status()

        try:
            data = resp.json()
        except Exception:
            data = {"raw_response": resp.text}

        result = {
            "vendor_id": vendor_id,
            "questionnaire_qna": data,
        }

        return json.dumps(result, default=str)

    except Exception as e:
        return handle_ariba_error(e)
      
      
            
