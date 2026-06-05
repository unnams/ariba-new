import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

CONFIGURATION_PARAMETER_REVIEW_API = "sourcing-config-parameter/v1/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_config_parameters_list",
        description=(
            "Retrieve a list of all configuration parameters and their current and default values "
            "for a SAP Ariba Sourcing or Buying realm. "
            "Useful for auditing parameter settings, detecting drift from defaults, "
            "or comparing test vs. production realm configurations."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def config_parameters_list(
        realm: str,
        filter: str | None = None,
        top: int | None = None,
        skip: int | None = None,
    ) -> str:
        try:
            params: dict = {"realm": realm}
            if filter:
                params["$filter"] = filter
            if top is not None:
                params["$top"] = top
            if skip is not None:
                params["$skip"] = skip
            result = await client.fetch_resource(
                CONFIGURATION_PARAMETER_REVIEW_API, "parameters", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_config_parameter_get",
        description=(
            "Retrieve a specific SAP Ariba configuration parameter by its exact name. "
            "Returns the current value set in the realm, the product default value, "
            "and whether the parameter has been modified from its default. "
            "Use ariba_config_parameters_list to discover valid parameter names."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def config_parameter_get(
        realm: str,
        parameter_name: str,
    ) -> str:
        try:
            params: dict = {"realm": realm}
            result = await client.fetch_resource(
                CONFIGURATION_PARAMETER_REVIEW_API,
                f"parameters/{parameter_name}",
                params,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)
