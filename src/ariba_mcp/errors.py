import json

import httpx

_FALLBACK_MESSAGES = {
    401: "Authentication failed. Check OAuth client_id/client_secret and apiKey.",
    403: "Access denied. Verify realm and API subscription for this endpoint.",
    404: "Resource not found. Verify the document/ID exists in this realm.",
    405: "Method not allowed. This endpoint may be read-only.",
    429: "Rate limit exceeded. Wait a moment and retry.",
    500: "Ariba server error. Retry later or check SAP status page.",
    503: "Ariba service unavailable. Retry later.",
}


def _extract_ariba_error(response: httpx.Response) -> dict:
    try:
        body = response.json()
    except Exception:
        text = response.text.strip()
        return {"raw": text[:1000]} if text else {}

    if isinstance(body, dict):
        if "error" in body and isinstance(body["error"], dict):
            err = body["error"]
            return {
                "errorCode": err.get("errorCode"),
                "message": err.get("message"),
                "description": err.get("description"),
            }
        if "message" in body or "error_description" in body or "error" in body:
            return {
                "message": body.get("message") or body.get("error_description"),
                "error": body.get("error"),
                "errorCode": body.get("errorCode") or body.get("code"),
            }
    return {"body": body}


def handle_ariba_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        ariba_error = _extract_ariba_error(e.response)
        result = {"error": True, "status": status}
        if ariba_error:
            result["ariba"] = ariba_error
        else:
            result["message"] = _FALLBACK_MESSAGES.get(status, f"Ariba API returned HTTP {status}.")
        return json.dumps(result, default=str)

    if isinstance(e, httpx.TimeoutException):
        return json.dumps({"error": True, "message": "Request timed out."})

    return json.dumps({"error": True, "message": f"{type(e).__name__}: {e}"})
