import os
from pathlib import Path

from fastmcp import FastMCP
from mcp.types import Icon
from starlette.requests import Request
from starlette.responses import FileResponse, Response

from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


from ariba_mcp.client import AribaClient
from ariba_mcp.config import get_settings
from ariba_mcp.prompts import register_all_prompts
from ariba_mcp.prompts.procurement import build_assistant_body
from ariba_mcp.tools import register_all_tools

_client = AribaClient(get_settings())

_LOGO_PATH = Path(__file__).resolve().parents[2] / "assets" / "logo.png"
_PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://ariba-mcp.onrender.com")

mcp = FastMCP(
    "ariba-mcp",
    instructions=build_assistant_body(),
    icons=[
        Icon(
            src=f"{_PUBLIC_BASE_URL}/logo.png",
            mimeType="image/png",
            sizes=["1024x1024"],
        ),
    ],
)


@mcp.custom_route("/logo.png", methods=["GET"])
async def serve_logo(_: Request) -> Response:
    if not _LOGO_PATH.exists():
        return Response(status_code=404)
    return FileResponse(_LOGO_PATH, media_type="image/png")


register_all_tools(mcp, _client)
register_all_prompts(mcp)



if __name__ == "__main__":
    mcp.run()
