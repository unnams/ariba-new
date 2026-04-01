"""Supplier Risk Engagements API.

Owner: Nitish SM
Prod URL: https://openapi.ariba.com/api/risk-engagement/v2/prod
Docs: https://help.sap.com/doc/892703b130354abbb5013c3587a08cb2/cloud/en-US/270c23ef0b584430aaf0d932755d3089.html

Gets control-based engagement risk assessment project data:
engagements, issues, modular and inherent risk screening questionnaires.

Authentication: OAuth 2.0 Bearer token + apiKey header (own credentials)
"""

import json

import httpx
from fastmcp import FastMCP

from ariba_mcp.auth import DirectAuthClient
from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_settings
from ariba_mcp.errors import handle_ariba_error

BASE_URL = "https://openapi.ariba.com/api/risk-engagement/v2/prod"


def _make_auth() -> DirectAuthClient:
    s = get_settings()
    return DirectAuthClient(
        client_id=s.ariba_risk_client_id,
        client_secret=s.ariba_risk_client_secret,
        api_key=s.ariba_risk_api_key,
        timeout=s.request_timeout,
    )


def register(mcp: FastMCP, client: AribaClient) -> None:
    """Register Supplier Risk Engagements API tools."""

    _auth = _make_auth()

    @mcp.tool(
        name="ariba_risk_engagement_list",
        description=(
            "List all risk engagement projects from the realm. "
            "Returns engagement ID, title, status, risk score, creation date, and owner. "
            "Supports optional pagination via top (page size) and skip (offset)."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_engagements(top: int = 100, skip: int = 0) -> str:
        try:
            headers = await _auth.get_headers()
            params = {
                "realm": client.realm,
                "$top": top,
                "$skip": skip,
            }
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/engagements",
                    headers=headers,
                    params=params,
                    timeout=60,
                )
                resp.raise_for_status()
            data = resp.json()
            return json.dumps(data, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_risk_engagement_get",
        description=(
            "Get details of a specific risk engagement project by engagement ID. "
            "Returns full engagement data including risk scores, questionnaire responses, "
            "issues, and screening results."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_engagement(engagement_id: str) -> str:
        try:
            headers = await _auth.get_headers()
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/engagements/{engagement_id}",
                    headers=headers,
                    params={"realm": client.realm},
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_risk_engagement_issues",
        description=(
            "List all issues for a specific risk engagement project. "
            "Returns issue ID, description, severity, status, and assigned owner."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_engagement_issues(engagement_id: str) -> str:
        try:
            headers = await _auth.get_headers()
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/engagements/{engagement_id}/issues",
                    headers=headers,
                    params={"realm": client.realm},
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_risk_engagement_questionnaires",
        description=(
            "Get risk screening questionnaire responses for a specific engagement. "
            "Returns both modular (control-based) and inherent risk questionnaire data."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_engagement_questionnaires(engagement_id: str) -> str:
        try:
            headers = await _auth.get_headers()
            async with httpx.AsyncClient() as http:
                resp = await http.get(
                    f"{BASE_URL}/engagements/{engagement_id}/questionnaires",
                    headers=headers,
                    params={"realm": client.realm},
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)
