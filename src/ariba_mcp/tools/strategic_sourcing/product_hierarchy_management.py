"""Product Hierarchy Management API.

Owner: Shabreen
Docs: https://help.sap.com/doc/27b5932567614e0eb559242fe24f57c4/cloud/en-US/index.html

This API retrieves product questionnaires responded to by a supplier, 
including details on associated sourcing events and line items.

Endpoints implemented:
  GET /productQuestionnaires – retrieve list of product questionnaires
"""

import json
from fastmcp import FastMCP
from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

# Note the v2 version in the path
PRODUCT_HIERARCHY_API = "product-hierarchy/v2/prod"

def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_product_questionnaires_list",
        description=(
            "Retrieve a list of product questionnaires responded to by a supplier. "
            "Includes data about associated sourcing events and specific line items."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def product_questionnaires_list(
        realm: str,
        filter: str | None = None,
        top: int | None = None,
        skip: int | None = None,
        count: bool | None = None,
    ) -> str:
        """
        Args:
            realm:   Required. The target SAP Ariba realm.
            filter:  Optional. OData $filter expression. 
                     Supported fields often include: supplierId, eventId, lineItemId.
            top:     Optional. Max records per page (default 10).
            skip:    Optional. Number of records to skip (offset).
            count:   Optional. If True, returns the total count of records.
        """
        try:
            params: dict = {"realm": realm}
            if filter:
                params["$filter"] = filter
            if top is not None:
                params["$top"] = top
            if skip is not None:
                params["$skip"] = skip
            if count is not None:
                params["$count"] = str(count).lower()

            result = await client.fetch_resource(
                PRODUCT_HIERARCHY_API, "productQuestionnaires", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)