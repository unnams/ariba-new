# Contributing to ariba-mcp

8 team members building an MCP server for 48 SAP Ariba APIs.

**API Docs:** https://help.sap.com/docs/ariba-apis
**Developer Portal:** https://developer.ariba.com

---

## Getting Started

```bash
git clone https://github.com/nitishsm2002/ariba-mcp.git
cd ariba-mcp
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

Get the `.env` file from the credentials owner and place it in the project root.

---

## How It Works

- **Shared infrastructure is done** — `config.py`, `auth.py`, `client.py`, `errors.py`, `server.py` are complete
- **Each tool file has one working example** and **TODO comments** for remaining APIs
- **You only edit your tool file** — find your API in the TODO list, implement it
- Each file is in `src/ariba_mcp/tools/` and grouped by domain

---

## Step-by-Step: Implement Your API

### 1. Find your file

| Domain File | APIs |
|------------|------|
| `tools/supplier_management.py` | Supplier Data, Profiles, Risk, Invite |
| `tools/procurement_reporting.py` | Operational & Analytical Reporting |
| `tools/sourcing.py` | Sourcing projects, events, approvals, master data |
| `tools/contracts.py` | Compliance, workspaces, terms, NDA, cost breakdown |
| `tools/purchase_orders.py` | PO buyer/supplier, order change requests |
| `tools/catalogs.py` | Internal/public/network catalogs, content |
| `tools/supply_chain.py` | Ship notice, planning, invoices, certifications |
| `tools/administration.py` | Approvals, audit, monitoring, config, forms |

### 2. Look up your API docs

Each file header lists the doc links. Also check:
- https://developer.ariba.com → log in → find your API → Swagger spec
- The Swagger spec gives you the **exact endpoint path** and **parameters**

### 3. Add your API path constant

```python
# At the top of the file, uncomment and fill in:
MY_API_PATH = "my-api/v1/prod"
```

### 4. Implement your tool

Copy the example tool in the file and modify:

```python
@mcp.tool(
    name="ariba_<meaningful_name>",
    description="Clear description of what this does.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def my_tool(param: str, page_token: str | None = None) -> str:
    try:
        result = await client.fetch_resource(MY_API_PATH, f"resource/{param}")
        return json.dumps(result, default=str)
    except Exception as e:
        return handle_ariba_error(e)
```

### 5. Test

```bash
# Start server
python -m ariba_mcp.server

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python -m ariba_mcp.server
```

---

## Client Methods Reference

The `AribaClient` (in `client.py`) provides these methods:

```python
# Reporting view queries (Operational/Analytical Reporting)
await client.fetch_view(api_path, view_name, filters_dict, page_token)
await client.fetch_view_count(api_path, view_name, filters_dict)

# Async jobs (large datasets)
await client.submit_job(job_api_path, view_name, filters_dict)
await client.get_job_status(job_api_path, job_id)
await client.get_job_results(result_api_path, job_id, page_token)

# REST resource APIs (Supplier Data, Contracts, etc.)
await client.fetch_resource(api_path, "resource/path", extra_params)

# Generic (if nothing else fits)
await client.get(full_url, params)
await client.post(full_url, json_body, params)
```

`client.realm` and `client.base_url` are available as properties.

---

## Branch Naming

```
feature/<api-name>         # e.g. feature/supplier-data-api
fix/<api-name>-<desc>      # e.g. fix/risk-exposure-pagination
chore/<desc>               # e.g. chore/update-deps
```

---

## PR Process

1. Branch from `main`
2. Implement your tool(s)
3. Run: `ruff check src/ && ruff format src/`
4. Push and open a PR
5. 1 reviewer approves → squash merge

---

## Rules

- **Async everywhere** — all tool functions are `async`
- **Always catch exceptions** — use `handle_ariba_error(e)`
- **Return JSON strings** — `json.dumps(result, default=str)`
- **Support pagination** — accept `page_token` where applicable
- **No secrets in code** — credentials from `.env` only
- **Tool names** — prefix with `ariba_`, use `snake_case`
- **Don't modify shared infra** without coordinating with the team
