# Contributing to ariba-mcp

Team of 8 working on the SAP Ariba MCP Server. Each member owns one API domain.

**API Reference:** https://help.sap.com/docs/ariba-apis
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

## Shared Credentials

One person manages the SAP Ariba Developer Portal application:

1. Registers the app at https://developer.ariba.com
2. Enables needed APIs for the test realm
3. Creates the `.env` file with `ARIBA_REALM`, `ARIBA_CLIENT_ID`, `ARIBA_CLIENT_SECRET`, `ARIBA_API_KEY`
4. Shares it securely with all 8 members

**Never commit `.env` to git.** If credentials rotate, the owner updates and redistributes.

---

## Domain Ownership

| Member | Domain | File | SAP Ariba APIs |
|--------|--------|------|----------------|
| 1 | Operational Procurement | `tools/operational_procurement.py` | Procurement Reporting (view, job, jobresult) |
| 2 | Operational Sourcing | `tools/operational_sourcing.py` | Sourcing Reporting views |
| 3 | Analytical Reporting | `tools/analytical_reporting.py` | Analytics Reporting (view, job, jobresult) |
| 4 | Supplier Data | `tools/supplier_data.py` | Supplier Data API, Supplier Profile API |
| 5 | Contracts | `tools/contract_compliance.py` | Contract Compliance, Workspace, Terms |
| 6 | Sourcing Projects | `tools/sourcing_project.py` | Sourcing Project Mgmt, Approvals, Master Data |
| 7 | Approvals & Audit | `tools/document_approval.py` | Document Approval, Audit Search, Monitoring |
| 8 | Supplier Risk | `tools/supplier_risk.py` | Risk Exposure, Engagements, Categories |

---

## Branch Naming

```
feature/<domain>           # e.g. feature/operational-procurement
fix/<domain>-<desc>        # e.g. fix/supplier-data-pagination
chore/<desc>               # e.g. chore/update-deps
```

Always branch from `main`. Keep branches short-lived.

---

## PR Process

1. Branch from `main`
2. Implement your changes in your domain file
3. Run checks:
   ```bash
   ruff check src/ tests/
   ruff format src/ tests/
   pytest
   ```
4. Push and open a PR
5. **1 reviewer** must approve before merge
6. Squash merge to `main`

---

## Coding Standards

### Tool Pattern
Every tool follows this pattern:
```python
@mcp.tool(
    name="ariba_<domain>_<action>",
    description="Clear description of what this tool does.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def my_tool(param: str, page_token: str | None = None) -> str:
    try:
        result = await client.fetch_view(API_PATH, view_name, filters, page_token)
        return json.dumps(result, default=str)
    except Exception as e:
        return handle_ariba_error(e)
```

### Key Rules
- **Async everywhere** — all functions are `async`
- **Always catch exceptions** — use `handle_ariba_error(e)`
- **Return JSON strings** — `json.dumps(result, default=str)`
- **Support pagination** — accept `page_token` parameter where applicable
- **No secrets in code** — credentials come from `.env` only
- **Tool names** — prefix with `ariba_`, use `snake_case`

### Using the Client

The `AribaClient` provides three patterns matching Ariba's API types:

```python
# 1. View-based queries (Reporting APIs)
result = await client.fetch_view(api_path, view_name, filters_dict, page_token)
count  = await client.fetch_view_count(api_path, view_name, filters_dict)

# 2. Async jobs (large datasets)
job    = await client.submit_job(job_api_path, view_name, filters_dict)
status = await client.get_job_status(job_api_path, job_id)
data   = await client.get_job_results(result_api_path, job_id, page_token)

# 3. Resource-based (Supplier Data, Contracts, etc.)
result = await client.fetch_resource(api_path, "resource/id", extra_params)
```

---

## How to Add a New Tool

1. Open your domain file (`src/ariba_mcp/tools/<your_domain>.py`)
2. Add a new `@mcp.tool(...)` function inside the `register()` function
3. Use the correct client method for your API type
4. Test with MCP Inspector:
   ```bash
   npx @modelcontextprotocol/inspector python -m ariba_mcp.server
   ```

## How to Add a New API Domain

1. Create `src/ariba_mcp/tools/<new_domain>.py` with a `register(mcp, client)` function
2. Add the import to `src/ariba_mcp/tools/__init__.py`
3. Add it to the `_DOMAINS` list

---

## Finding Your API Documentation

Each domain maps to specific APIs on the SAP Ariba Developer Portal:

1. Go to https://developer.ariba.com
2. Find your API by name (see table above)
3. Check the Swagger/OpenAPI spec for:
   - Exact endpoint paths
   - Required/optional parameters
   - Response schemas
   - View template names

Also refer to: https://help.sap.com/docs/ariba-apis

---

## Shared Infrastructure

| File | What It Does | Change Carefully |
|------|-------------|------------------|
| `server.py` | MCP entrypoint + lifespan | Affects all domains |
| `config.py` | Environment settings | Adding new env vars |
| `auth.py` | OAuth token management | Auth flow changes |
| `client.py` | HTTP client (view, job, resource) | API call patterns |
| `errors.py` | Error handling | Error message changes |
| `tools/__init__.py` | Domain registration | Adding new domains |

Coordinate on Slack/Teams before modifying shared files.
