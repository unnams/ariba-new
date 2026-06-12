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
            "Use page and page_size to paginate through results."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
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
            "Pass one or more SM Vendor IDs comma-separated."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
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
        name="ariba_supplier_questionnaire_qna",
        description=(
            "Fetch supplier workspace questionnaire Q&A data from SAP Ariba "
            "Supplier Data Pagination API for a given supplier/vendor ID."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def supplier_questionnaire_qna(vendor_id: str) -> str:
        try:
            url = (
                f"{client.base_url}/{API_PATH}/vendors/"
                f"{vendor_id}/workspaces/questionnaires/qna"
            )

            headers = await _sdp_auth.get_headers()
            headers["Accept"] = "application/json"

            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    url,
                    params={"realm": client.realm},
                    headers=headers,
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
