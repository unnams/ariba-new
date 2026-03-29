"""OAuth 2.0 client-credentials authentication for SAP Ariba APIs.

Endpoint: POST {oauth_url}/v2/oauth/token?grant_type=client_credentials
Auth:     HTTP Basic (client_id:client_secret)
Docs:     https://help.sap.com/docs/ariba-apis/help-for-sap-ariba-developer-portal/making-of-rest-api-calls-with-oauth-access-token-and-application-key
"""

import asyncio
import time

import httpx

from ariba_mcp.config import AribaSettings


class AribaAuthClient:
    """Manages OAuth token acquisition and caching for Ariba APIs."""

    def __init__(self, settings: AribaSettings, http_client: httpx.AsyncClient) -> None:
        self._settings = settings
        self._http = http_client
        self._token: str | None = None
        self._expires_at: float = 0
        self._lock = asyncio.Lock()

    async def get_token(self) -> str:
        """Return a valid access token, refreshing if expired."""
        async with self._lock:
            if self._token and time.time() < (self._expires_at - 60):
                return self._token

            response = await self._http.post(
                f"{self._settings.ariba_oauth_url}/v2/oauth/token",
                data={"grant_type": "client_credentials"},
                auth=(self._settings.ariba_client_id, self._settings.ariba_client_secret),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            data = response.json()

            self._token = data["access_token"]
            self._expires_at = time.time() + data.get("expires_in", 1440)
            return self._token

    async def get_headers(self) -> dict[str, str]:
        """Return header set for an authenticated Ariba API request."""
        token = await self.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "apiKey": self._settings.ariba_api_key,
            "Accept": "application/json",
        }
