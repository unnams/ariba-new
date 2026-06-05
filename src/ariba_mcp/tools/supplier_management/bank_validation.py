import json
import re

import httpx
from fastmcp import FastMCP

from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

IFSC_URL = "https://ifsc.razorpay.com/{ifsc}"
ACCOUNT_REGEX = re.compile(r"^\d{9,18}$")


def register(mcp: FastMCP, client: AribaClient) -> None:

    @mcp.tool(
        name="ariba_bank_validate_ifsc",
        description=(
            "Validate an Indian bank IFSC code and retrieve branch details. "
            "Returns bank name, branch, city, address, contact, and MICR code. "
            "Example: HDFC0001234"
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def validate_ifsc(ifsc: str) -> str:
        try:
            ifsc = ifsc.strip().upper()
            async with httpx.AsyncClient() as http:
                resp = await http.get(IFSC_URL.format(ifsc=ifsc), timeout=10)
                if resp.status_code == 404:
                    return json.dumps({"valid": False, "ifsc": ifsc, "error": "IFSC code not found"})
                resp.raise_for_status()
            return json.dumps({"valid": True, "ifsc": ifsc, "details": resp.json()}, default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_bank_validate_account_format",
        description="Validate Indian bank account number format (9–18 digits, numeric only).",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    )
    async def validate_account_format(account_number: str) -> str:
        account_number = account_number.strip()
        valid = bool(ACCOUNT_REGEX.match(account_number))
        return json.dumps({
            "account_number": account_number,
            "valid": valid,
            "reason": "OK" if valid else "Account number must be 9–18 digits (numeric only)",
        })

    @mcp.tool(
        name="ariba_bank_validate_full",
        description=(
            "Validate both IFSC code and account number format. "
            "Returns validity of each and branch details if IFSC is valid."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def validate_full(ifsc: str, account_number: str) -> str:
        try:
            ifsc = ifsc.strip().upper()
            account_number = account_number.strip()
            account_valid = bool(ACCOUNT_REGEX.match(account_number))

            async with httpx.AsyncClient() as http:
                resp = await http.get(IFSC_URL.format(ifsc=ifsc), timeout=10)
                if resp.status_code == 404:
                    ifsc_valid, ifsc_details = False, None
                else:
                    resp.raise_for_status()
                    ifsc_valid, ifsc_details = True, resp.json()

            return json.dumps({
                "ifsc": {"code": ifsc, "valid": ifsc_valid, "details": ifsc_details},
                "account_number": {"number": account_number, "valid": account_valid},
                "overall_valid": ifsc_valid and account_valid,
            }, default=str)
        except Exception as e:
            return handle_ariba_error(e)
