"""Asset Management API tools."""


import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

ASSET_MANAGEMENT_API = "asset-management"
ASSET_MANAGEMENT_API_NAME = "asset_management"


def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_asset_list_requisitions",
        description=(
            "List SAP Ariba purchase requisitions that contain asset line items. "
            "Supports optional date filters and pagination."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def asset_list_requisitions(
        time_created: str | None = None,
        time_updated: str | None = None,
        top: int = 50,
        skip: int = 0,
    ) -> str:
        """
        Args:
            time_created: Filter by creation date (ISO-8601), for example '2024-01-01T00:00:00Z'.
            time_updated: Filter by last-updated date (ISO-8601), for example '2024-06-01T00:00:00Z'.
            top: Maximum number of records to return (default 50).
            skip: Number of records to skip for pagination (default 0).
        """
        try:
            params: dict[str, int | str] = {"$top": top, "$skip": skip}

            filters: list[str] = []
            if time_created:
                filters.append(f"TimeCreated eq {time_created}")
            if time_updated:
                filters.append(f"TimeUpdated eq {time_updated}")
            if filters:
                params["$filter"] = ";".join(filters)

            result = await client.fetch_resource(
                ASSET_MANAGEMENT_API,
                "requisitions",
                params,
                api_name=ASSET_MANAGEMENT_API_NAME,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_asset_count_requisitions",
        description=(
            "Return the total count of SAP Ariba requisitions that contain asset line items. "
            "Useful before paginating through large result sets."
        ),
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def asset_count_requisitions(
        time_created: str | None = None,
        time_updated: str | None = None,
    ) -> str:
        """
        Args:
            time_created: Filter by creation date (ISO-8601), for example '2024-01-01T00:00:00Z'.
            time_updated: Filter by last-updated date (ISO-8601), for example '2024-06-01T00:00:00Z'.
        """
        try:
            params: dict[str, str] = {}

            filters: list[str] = []
            if time_created:
                filters.append(f"TimeCreated eq {time_created}")
            if time_updated:
                filters.append(f"TimeUpdated eq {time_updated}")
            if filters:
                params["$filter"] = ";".join(filters)

            result = await client.fetch_resource(
                ASSET_MANAGEMENT_API,
                "requisitions/$count",
                params,
                api_name=ASSET_MANAGEMENT_API_NAME,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_asset_update_line_items",
        description=(
            "Assign or update asset numbers on asset line items inside an SAP Ariba requisition. "
            "Use after a requisition is approved to tag physical assets to line items."
        ),
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def asset_update_line_items(
        requisition_id: str,
        number_in_collection: int,
        asset_number: str,
        serial_number: str | None = None,
        description: str | None = None,
    ) -> str:
        """
        Args:
            requisition_id: Unique ID of the requisition (for example 'PR-123456').
            number_in_collection: Line item number inside the requisition.
            asset_number: Asset number to assign (for example 'AST-0001').
            serial_number: Optional serial number of the physical asset.
            description: Optional short description of the asset.
        """
        try:
            asset: dict[str, str] = {"AssetNumber": asset_number}
            if serial_number:
                asset["SerialNumber"] = serial_number
            if description:
                asset["Description"] = description

            payload = {
                "requisitions": [
                    {
                        "RequisitionId": requisition_id,
                        "AssetLineItems": [
                            {
                                "NumberInCollection": number_in_collection,
                                "Action": "update",
                                "Assets": [asset],
                            }
                        ],
                    }
                ]
            }

            result = await client.post_resource(
                ASSET_MANAGEMENT_API,
                "requisitions/batch/assets",
                payload,
                api_name=ASSET_MANAGEMENT_API_NAME,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)