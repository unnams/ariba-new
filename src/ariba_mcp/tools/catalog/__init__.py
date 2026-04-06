from fastmcp import FastMCP

from ariba_mcp.client import AribaClient


def register(mcp: FastMCP, client: AribaClient) -> None:
    from ariba_mcp.tools.catalog import (
        content_lookup,
        internal_catalogs_shop,
        public_catalogs_shop,
    )

    content_lookup.register(mcp, client)
    internal_catalogs_shop.register(mcp, client)
    public_catalogs_shop.register(mcp, client)
