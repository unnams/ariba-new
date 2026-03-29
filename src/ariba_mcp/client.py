"""Base HTTP client for SAP Ariba APIs.

Supports two API patterns used by Ariba:

1. Synchronous (view-based):
   GET {base}/views/{viewName}?realm={realm}&filters={json}
   Used by: Operational Reporting, Analytical Reporting, Supplier Data, etc.

2. Synchronous (resource-based):
   GET {base}/{resource}?realm={realm}&...
   Used by: Contract Compliance, Sourcing Approval, Document Approval, etc.

Pagination:
- Async/view APIs use pageToken (returned in response body)
- Sync APIs use $skip/$top or pageToken depending on the API
"""

from typing import Any

import httpx

from ariba_mcp.auth import AribaAuthClient
from ariba_mcp.config import AribaSettings


class AribaClient:
    """Async HTTP client for SAP Ariba REST APIs."""

    def __init__(self, settings: AribaSettings, http_client: httpx.AsyncClient) -> None:
        self._settings = settings
        self._http = http_client
        self.auth = AribaAuthClient(settings, http_client)

    @property
    def realm(self) -> str:
        return self._settings.ariba_realm

    @property
    def base_url(self) -> str:
        return self._settings.ariba_api_url

    async def get(self, url: str, params: dict[str, Any] | None = None) -> dict:
        """Send an authenticated GET to a full URL."""
        headers = await self.auth.get_headers()
        response = await self._http.get(
            url, headers=headers, params=params, timeout=self._settings.request_timeout
        )
        response.raise_for_status()
        return response.json()

    async def post(self, url: str, json_body: dict | None = None, params: dict[str, Any] | None = None) -> dict:
        """Send an authenticated POST."""
        headers = await self.auth.get_headers()
        response = await self._http.post(
            url, headers=headers, json=json_body, params=params, timeout=self._settings.request_timeout
        )
        response.raise_for_status()
        return response.json()

    # ── View-based APIs (Operational / Analytical Reporting) ──

    async def fetch_view(
        self,
        api_path: str,
        view_name: str,
        filters: dict | None = None,
        page_token: str | None = None,
    ) -> dict:
        """Fetch a reporting view with optional filters and pagination.

        Args:
            api_path: API base path, e.g. "procurement-reporting-details/v1/prod"
            view_name: View template name, e.g. "CostCenterProcurementSystemView"
            filters: Optional filter dict (e.g. {"createdDateFrom": "2025-01-01"})
            page_token: Token for next page (from previous response)

        Returns:
            Raw API response dict containing records and optional pageToken.
        """
        import json as json_mod

        url = f"{self.base_url}/{api_path}/views/{view_name}"
        params: dict[str, Any] = {"realm": self.realm}
        if filters:
            params["filters"] = json_mod.dumps(filters)
        if page_token:
            params["pageToken"] = page_token
        return await self.get(url, params)

    async def fetch_view_count(self, api_path: str, view_name: str, filters: dict | None = None) -> dict:
        """Get the record count for a reporting view."""
        import json as json_mod

        url = f"{self.base_url}/{api_path}/views/{view_name}/count"
        params: dict[str, Any] = {"realm": self.realm}
        if filters:
            params["filters"] = json_mod.dumps(filters)
        return await self.get(url, params)

    # ── Job-based APIs (Async Reporting) ──

    async def submit_job(self, api_path: str, view_name: str, filters: dict | None = None) -> dict:
        """Submit an async reporting job.

        Args:
            api_path: e.g. "procurement-reporting-job/v2/prod"
            view_name: View template name
            filters: Optional filter criteria
        """
        url = f"{self.base_url}/{api_path}/jobs"
        params: dict[str, Any] = {"realm": self.realm}
        body: dict[str, Any] = {"viewTemplateName": view_name}
        if filters:
            body["filters"] = filters
        return await self.post(url, json_body=body, params=params)

    async def get_job_status(self, api_path: str, job_id: str) -> dict:
        """Check status of an async reporting job."""
        url = f"{self.base_url}/{api_path}/jobs/{job_id}"
        return await self.get(url, {"realm": self.realm})

    async def get_job_results(self, api_path: str, job_id: str, page_token: str | None = None) -> dict:
        """Fetch results of a completed async job."""
        params: dict[str, Any] = {"realm": self.realm}
        if page_token:
            params["pageToken"] = page_token
        url = f"{self.base_url}/{api_path}/jobs/{job_id}"
        return await self.get(url, params)

    # ── Resource-based APIs (Contract Compliance, Approvals, etc.) ──

    async def fetch_resource(self, api_path: str, resource: str, params: dict[str, Any] | None = None) -> dict:
        """Fetch a resource endpoint.

        Args:
            api_path: e.g. "contract-compliance/v1/prod"
            resource: e.g. "contracts/ABC123"
            params: Additional query parameters
        """
        url = f"{self.base_url}/{api_path}/{resource}"
        all_params: dict[str, Any] = {"realm": self.realm}
        if params:
            all_params.update(params)
        return await self.get(url, all_params)
