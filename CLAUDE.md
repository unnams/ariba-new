# Project Ground Truth

## Tech Stack

Python 3.11+, FastMCP, httpx, Pydantic, pydantic-settings

## Environment Variables

_Source: .env.example_

ARIBA_REALM, ARIBA_CLIENT_ID, ARIBA_CLIENT_SECRET, ARIBA_API_KEY

## Project Structure

```
src/
  ariba_mcp/
    models/
      __init__.py
      common.py
    tools/
      __init__.py
      supplier_management.py
      procurement_reporting.py
      sourcing.py
      contracts.py
      purchase_orders.py
      catalogs.py
      supply_chain.py
      administration.py
    __init__.py
    auth.py
    client.py
    config.py
    errors.py
    server.py
```
