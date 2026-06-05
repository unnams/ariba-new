import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

PRODUCT_HIERARCHY_API = "product-hierarchy/v2/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_product_questionnaires_list",
        description=(
            "Retrieve a list of product questionnaires responded to by suppliers in SAP Ariba. "
            "Includes data about associated sourcing events. Supports filtering and pagination."
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

    @mcp.tool(
        name="ariba_product_questionnaire_get",
        description=(
            "Retrieve a specific product questionnaire by its ID from SAP Ariba. "
            "Returns full details of the questionnaire including supplier responses."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def product_questionnaire_get(
        realm: str,
        questionnaire_id: str,
    ) -> str:
        try:
            params: dict = {"realm": realm}
            result = await client.fetch_resource(
                PRODUCT_HIERARCHY_API,
                f"productQuestionnaires/{questionnaire_id}",
                params,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_product_questionnaire_line_items_list",
        description=(
            "Retrieve line items for a specific product questionnaire from SAP Ariba. "
            "Returns item-level details including commodity codes, descriptions, "
            "and sourcing event line item associations."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def product_questionnaire_line_items_list(
        realm: str,
        questionnaire_id: str,
        top: int | None = None,
        skip: int | None = None,
    ) -> str:
        try:
            params: dict = {"realm": realm}
            if top is not None:
                params["$top"] = top
            if skip is not None:
                params["$skip"] = skip
            result = await client.fetch_resource(
                PRODUCT_HIERARCHY_API,
                f"productQuestionnaires/{questionnaire_id}/lineItems",
                params,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)
