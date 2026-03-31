"""Supplier Information API.

Owner: Shabreen
Docs: https://help.sap.com/doc/8755ad14edb74721a039337c0c01edf2/cloud/en-US/index.html

This API allows buyer applications to verify if a relationship exists with a 
supplier on the SAP Business Network for specific collaboration types.

Endpoints implemented:
  GET /suppliers – retrieve supplier relationship and collaboration details

Prerequisites:
  - SAP Ariba Developer Portal access
  - OAuth authentication configured
  - API client ID configured in SAP Business Network for buyers
"""

import json
from fastmcp import FastMCP
from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

SUPPLIER_INFORMATION_API = "supplier-information/v1/prod"

def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_supplier_information_list",
        description=(
            "Verify buyer-supplier relationships and collaboration types on SAP Business Network. "
            "Returns details about suppliers linked to the buyer, including their ANID and "
            "enabled collaboration features (e.g., Supply Chain, Forecast)."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def supplier_information_list(
        anid: str,
        filter: str | None = None,
        top: int | None = None,
        skip: int | None = None,
    ) -> str:
        """
        Args:
            anid:    Required. The Buyer's Ariba Network ID (ANID).
            filter:  Optional. OData $filter expression. Supported fields:
                       supplierANID, collaborationType, vendorId
                     Example: 
                       "supplierANID eq AN01000000123"
                       "collaborationType eq SUPPLY_CHAIN"
            top:     Optional. Max records per page (default 10, max 100).
            skip:    Optional. Number of records to skip (offset).
        """
        try:
            # The API requires the buyer's ANID in the headers (handled by client) 
            # and supports standard OData parameters.
            params: dict = {"anid": anid}
            if filter:
                params["$filter"] = filter
            if top is not None:
                params["$top"] = top
            if skip is not None:
                params["$skip"] = skip

            result = await client.fetch_resource(
                SUPPLIER_INFORMATION_API, "suppliers", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)