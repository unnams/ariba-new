import json

import httpx
from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

API_PATH = "contentlookup/v1/prod"
BASE_URL = "https://openapi.ariba.com/api/contentlookup/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_content_lookup_update",
        description=(
            "Update an existing lookup in the SAP Ariba content management system (CMS). "
            "Uploads a lookup file for a given lookup name. "
            "Returns a unique lookup version ID if the upload was accepted. "
            "Note: this does not create new lookups — the lookup must already exist in the solution."
        ),
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def content_lookup_update(
        lookup_name: str,
        file_content: str,
        file_name: str = "lookup.csv",
    ) -> str:
        try:
            url = f"{BASE_URL}/lookup"
            headers = await client.auth.get_headers()
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    url,
                    params={"lookupname": lookup_name},
                    headers=headers,
                    files={"File": (file_name, file_content.encode("utf-8"), "text/csv")},
                    timeout=60,
                )
                resp.raise_for_status()
                try:
                    return json.dumps(resp.json(), default=str)
                except ValueError:
                    return resp.text
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_content_lookup_get_status",
        description=(
            "Fetch the status of a lookup by name, optionally narrowed to a specific version ID. "
            "If `lookup_id` is omitted, the API returns all known versions for that lookup."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def content_lookup_get_status(
        lookup_name: str, lookup_id: str | None = None
    ) -> str:
        try:
            url = f"{BASE_URL}/lookup"
            headers = await client.auth.get_headers()
            params = {"lookupname": lookup_name}
            if lookup_id:
                params["id"] = lookup_id
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=60,
                )
                resp.raise_for_status()
                try:
                    return json.dumps(resp.json(), default=str)
                except ValueError:
                    return resp.text
        except Exception as e:
            return handle_ariba_error(e)
