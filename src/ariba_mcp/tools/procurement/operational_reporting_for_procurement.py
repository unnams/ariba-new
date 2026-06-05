import json

from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

VIEW_MANAGEMENT_API  = "procurement-reporting-view/v2/prod"
JOB_SUBMISSION_API   = "procurement-reporting-job/v2/prod"
JOB_RESULT_API       = "procurement-reporting-jobresult/v2/prod"
SYNCHRONOUS_API      = "procurement-reporting-details/v2/prod"


def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_procurement_view_templates_list",
        description=(
            "List all reporting view templates available for the realm in the "
            "Operational Reporting API for Procurement. Returns both system "
            "(built-in) and custom view templates. Use this to discover valid "
            "viewTemplateName values before submitting jobs or querying data."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def procurement_view_templates_list(
        realm: str,
        product: str = "buyer",
        include_inactive: bool = False,
    ) -> str:
        try:
            params: dict = {
                "realm": realm,
                "product": product,
                "includeInactive": str(include_inactive).lower(),
            }
            result = await client.fetch_resource(
                VIEW_MANAGEMENT_API, "viewTemplates", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_procurement_view_template_get",
        description=(
            "Retrieve the definition of a specific reporting view template by name "
            "from the Operational Reporting API for Procurement. Returns the "
            "document type, select attributes, and filter criteria for the template."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def procurement_view_template_get(
        realm: str,
        view_template_name: str,
        product: str = "buyer",
    ) -> str:
        try:
            params: dict = {"realm": realm, "product": product}
            result = await client.fetch_resource(
                VIEW_MANAGEMENT_API,
                f"viewTemplates/{view_template_name}",
                params,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_procurement_view_template_create",
        description=(
            "Create a new custom reporting view template in the Operational Reporting "
            "API for Procurement. A view template defines the document type, the fields "
            "to select, and the filter criteria for data extraction. "
            "Templates must be 'published' before use in jobs or synchronous queries. "
            "Use ariba_procurement_metadata_get first to discover available fields."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
    )
    async def procurement_view_template_create(
        realm: str,
        view_template_name: str,
        body: dict,
    ) -> str:
        try:
            result = await client.post_resource(
                VIEW_MANAGEMENT_API,
                f"viewTemplates/{view_template_name}",
                {"realm": realm},
                body,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_procurement_view_template_update",
        description=(
            "Update an existing custom reporting view template in the Operational "
            "Reporting API for Procurement. Use this to modify fields, filters, or "
            "status (publish/deactivate) of an existing template. "
            "Valid status values: 'published', 'deactivated'."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
    )
    async def procurement_view_template_update(
        realm: str,
        view_template_name: str,
        body: dict,
    ) -> str:
        try:
            result = await client.post_resource(
                VIEW_MANAGEMENT_API,
                f"viewTemplates/{view_template_name}/patch",
                {"realm": realm},
                body,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_procurement_metadata_get",
        description=(
            "Retrieve metadata for a specific document type in the Operational Reporting "
            "API for Procurement. Returns all available select fields and filter fields "
            "that can be used when creating a custom view template. "
            "Always call this before creating a new view template for a document type."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def procurement_metadata_get(
        realm: str,
        document_type: str,
        product: str = "buyer",
        include_custom_fields: bool = False,
    ) -> str:
        try:
            params: dict = {
                "realm": realm,
                "documentType": document_type,
                "product": product,
                "includeCustomFields": str(include_custom_fields).lower(),
            }
            result = await client.fetch_resource(
                VIEW_MANAGEMENT_API, "metadata", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_procurement_reporting_job_submit",
        description=(
            "Submit an asynchronous reporting job to the Operational Reporting API "
            "for Procurement. The job extracts data according to the specified view "
            "template and date filters. After submission, poll "
            "ariba_procurement_reporting_job_status until status is 'completed', "
            "'completedZeroRecords', or 'expired', then download using "
            "ariba_procurement_reporting_job_file_download. "
            "Rate limit: max 8 jobs/hour, 40 jobs/day."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
    )
    async def procurement_reporting_job_submit(
        realm: str,
        view_template_name: str,
        created_date_from: str,
        created_date_to: str,
        include_inactive: bool = False,
        page_token: str | None = None,
    ) -> str:
        try:
            params: dict = {
                "realm": realm,
                "includeInactive": str(include_inactive).lower(),
            }
            if page_token:
                params["pageToken"] = page_token
            body = {
                "viewTemplateName": view_template_name,
                "filters": {
                    "createdDateFrom": created_date_from,
                    "createdDateTo": created_date_to,
                },
            }
            result = await client.post_resource(
                JOB_SUBMISSION_API, "jobs", params, body
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_procurement_reporting_job_status",
        description=(
            "Check the status of a previously submitted async reporting job in the "
            "Operational Reporting API for Procurement. Poll this every 5 minutes "
            "after submitting a job via ariba_procurement_reporting_job_submit. "
            "Job statuses: 'pending' → 'processing' → 'completed' / "
            "'completedZeroRecords' / 'expired'. "
            "When 'completed', response includes file IDs to download."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def procurement_reporting_job_status(
        realm: str,
        job_id: str,
    ) -> str:
        try:
            params: dict = {"realm": realm}
            result = await client.fetch_resource(
                JOB_RESULT_API, f"jobs/{job_id}", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_procurement_reporting_job_file_download",
        description=(
            "Download a result file from a completed async reporting job in the "
            "Operational Reporting API for Procurement. A completed job may contain "
            "multiple ZIP files — call this for each fileId returned in the job status "
            "response. Each ZIP contains the extracted data in JSON format. "
            "Only call this when job status is 'completed'."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def procurement_reporting_job_file_download(
        realm: str,
        job_id: str,
        file_id: str,
        include_inactive: bool = False,
    ) -> str:
        try:
            params: dict = {
                "realm": realm,
                "includeInactive": str(include_inactive).lower(),
            }
            result = await client.fetch_resource(
                JOB_RESULT_API, f"jobs/{job_id}/files/{file_id}", params
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_procurement_reporting_sync_get",
        description=(
            "Synchronously retrieve procurement reporting data using a published view "
            "template from the Operational Reporting API for Procurement. "
            "Returns results immediately with pagination via pageToken. "
            "Recommended only for small datasets — for large extractions use the async "
            "job workflow (ariba_procurement_reporting_job_submit). "
            "Rate limit: max 3 requests/min, 50/hr, 300/day."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def procurement_reporting_sync_get(
        realm: str,
        view_template_name: str,
        filters: str | None = None,
        page_token: str | None = None,
    ) -> str:
        try:
            params: dict = {"realm": realm}
            if filters:
                params["filters"] = filters
            if page_token:
                params["pageToken"] = page_token
            result = await client.fetch_resource(
                SYNCHRONOUS_API,
                f"views/{view_template_name}",
                params,
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return handle_ariba_error(e)
