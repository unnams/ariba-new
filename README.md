# SAP Ariba MCP Server

A **Model Context Protocol (MCP) server** that exposes SAP Ariba's procurement APIs as Claude-compatible tools. Built with Python and [FastMCP](https://github.com/jlowin/fastmcp).

This enables Claude (or any MCP-compatible AI) to query procurement reporting data, sourcing projects, supplier information, contract compliance, approval workflows, and more — all via natural language.

**API Reference:** https://help.sap.com/docs/ariba-apis
**Developer Portal:** https://developer.ariba.com

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Consumer Layer                                  │
│  Claude Desktop / Claude Code / Custom App       │
└────────────────────┬────────────────────────────┘
                     │ MCP (stdio)
┌────────────────────▼────────────────────────────┐
│  ariba-mcp Server (this project)                 │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 8 Tool   │  │ Auth     │  │ Client   │       │
│  │ Domains  │──│ OAuth2.0 │──│ httpx    │       │
│  │ 35+ tools│  │ cached   │  │ async    │       │
│  └──────────┘  └──────────┘  └────┬─────┘       │
└────────────────────────────────────┼─────────────┘
                                     │ HTTPS
┌────────────────────────────────────▼─────────────┐
│  SAP Ariba APIs                                   │
│  OAuth: api.ariba.com                             │
│  Data:  openapi.ariba.com/api                     │
└──────────────────────────────────────────────────┘
```

---

## SAP Ariba APIs Covered

These map directly to the APIs on the [SAP Ariba Developer Portal](https://developer.ariba.com):

| # | Domain | API Base Path | Tools | Owner |
|---|--------|--------------|-------|-------|
| 1 | **Operational Procurement Reporting** | `procurement-reporting-*/v*/prod` | 7 | Member 1 |
| 2 | **Operational Sourcing Reporting** | `sourcing-reporting-view/v1/prod` | 4 | Member 2 |
| 3 | **Analytical Reporting** | `analytics-reporting-*/v1/prod` | 5 | Member 3 |
| 4 | **Supplier Data & Profiles** | `supplier-data/v4/prod`, `supplier-profile/v1/prod` | 5 | Member 4 |
| 5 | **Contract Compliance & Workspaces** | `contract-compliance/v1/prod`, `contract-workspace/v1/prod` | 5 | Member 5 |
| 6 | **Sourcing Project Management** | `sourcing-project/v1/prod`, `sourcing-approval/v2/prod` | 4 | Member 6 |
| 7 | **Document Approval & Audit** | `document-approval/v1/prod`, `audit-search/v1/prod` | 4 | Member 7 |
| 8 | **Supplier Risk** | `risk-exposure/v1/prod`, `risk-engagements/v1/prod` | 4 | Member 8 |

All tools are **read-only** and return **paginated JSON** with `pageToken` support.

---

## Prerequisites

- **Python 3.11+**
- **uv** (recommended) or pip
- **SAP Ariba API credentials** — one person sets this up for the whole team

---

## Credential Setup (One-time, by one team member)

One team member registers the application and shares credentials with everyone:

### Step 1: Register on SAP Ariba Developer Portal

1. Go to https://developer.ariba.com
2. Log in with your SAP account
3. Register a new application
4. Enable the APIs needed (Operational Reporting, Supplier Data, etc.)
5. Note down:
   - **OAuth Client ID** and **Client Secret**
   - **Application Key** (API Key)
   - **Realm** name (e.g. `mycompany-T` for test realm)

### Step 2: Share credentials

Create a `.env` file and share it securely with all team members:

```bash
cp .env.example .env
# Fill in the credentials from Step 1
```

```env
ARIBA_REALM=mycompany-T
ARIBA_CLIENT_ID=abc123...
ARIBA_CLIENT_SECRET=xyz789...
ARIBA_API_KEY=def456...
```

> **Never commit `.env` to git.** It's already in `.gitignore`.

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/nitishsm2002/ariba-mcp.git
cd ariba-mcp

# Using uv (recommended)
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Or using pip
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Add your `.env` file

Get the `.env` file from the team member who set up the credentials (see above).

### 3. Run the server

```bash
python -m ariba_mcp.server
```

### 4. Connect to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ariba": {
      "command": "python",
      "args": ["-m", "ariba_mcp.server"],
      "cwd": "/path/to/ariba-mcp"
    }
  }
}
```

> The server reads credentials from `.env` automatically. No need to put secrets in the Claude config.

### 5. Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python -m ariba_mcp.server
```

---

## Tool Reference

### Operational Procurement Reporting (7 tools)

| Tool | Description |
|------|-------------|
| `ariba_procurement_list_views` | List available procurement view templates |
| `ariba_procurement_get_view_metadata` | Get schema for a specific view |
| `ariba_procurement_query_view` | Query a view (POs, invoices, receipts, payments, etc.) |
| `ariba_procurement_count_view` | Get record count for a view |
| `ariba_procurement_submit_job` | Submit async job for large datasets |
| `ariba_procurement_get_job_status` | Check async job status |
| `ariba_procurement_get_job_results` | Fetch async job results |

### Operational Sourcing Reporting (4 tools)

| Tool | Description |
|------|-------------|
| `ariba_sourcing_query_view` | Query any sourcing reporting view |
| `ariba_sourcing_count_view` | Get record count for a sourcing view |
| `ariba_sourcing_list_projects` | List sourcing projects (shortcut) |
| `ariba_sourcing_list_requests` | List sourcing requests (shortcut) |

### Analytical Reporting (5 tools)

| Tool | Description |
|------|-------------|
| `ariba_analytics_query_view` | Query analytical reporting views |
| `ariba_analytics_count_view` | Get record count |
| `ariba_analytics_submit_job` | Submit async analytics job |
| `ariba_analytics_get_job_status` | Check job status |
| `ariba_analytics_get_job_results` | Fetch job results |

### Supplier Data (5 tools)

| Tool | Description |
|------|-------------|
| `ariba_supplier_list` | List all suppliers |
| `ariba_supplier_get` | Get supplier details by ID |
| `ariba_supplier_search` | Search by name/ID/status |
| `ariba_supplier_get_profile` | Get Ariba Network profile |
| `ariba_supplier_get_qualifications` | Get certifications/qualifications |

### Contract Compliance (5 tools)

| Tool | Description |
|------|-------------|
| `ariba_contract_list_workspaces` | List contract workspaces |
| `ariba_contract_get_workspace` | Get workspace details |
| `ariba_contract_check_compliance` | List compliance status |
| `ariba_contract_get_compliance` | Get compliance for specific contract |
| `ariba_contract_get_terms` | Get contract terms |

### Sourcing Project Management (4 tools)

| Tool | Description |
|------|-------------|
| `ariba_sourcing_get_project` | Get sourcing project details |
| `ariba_sourcing_get_workspace` | Get approval workspace by SR number |
| `ariba_sourcing_get_masterdata` | Retrieve sourcing master data |
| `ariba_sourcing_list_events` | List events for a project |

### Document Approval & Audit (4 tools)

| Tool | Description |
|------|-------------|
| `ariba_approval_list_pending` | List pending approvals |
| `ariba_approval_get_document` | Get approval details |
| `ariba_audit_search` | Search audit logs |
| `ariba_transaction_monitor` | Monitor transactions |

### Supplier Risk (4 tools)

| Tool | Description |
|------|-------------|
| `ariba_risk_get_exposure` | Get risk exposure for a supplier |
| `ariba_risk_list_exposures` | List all risk exposures |
| `ariba_risk_list_engagements` | List risk engagements |
| `ariba_risk_get_categories` | Get risk category taxonomy |

---

## Configuration Reference

| Environment Variable | Required | Default | Description |
|---------------------|----------|---------|-------------|
| `ARIBA_REALM` | Yes | — | Ariba realm (e.g. `mycompany-T`) |
| `ARIBA_CLIENT_ID` | Yes | — | OAuth 2.0 client ID |
| `ARIBA_CLIENT_SECRET` | Yes | — | OAuth 2.0 client secret |
| `ARIBA_API_KEY` | Yes | — | Application key from developer portal |
| `ARIBA_OAUTH_URL` | No | `https://api.ariba.com` | OAuth token endpoint base |
| `ARIBA_API_URL` | No | `https://openapi.ariba.com/api` | API base URL |
| `ARIBA_REQUEST_TIMEOUT` | No | `30` | HTTP timeout (seconds) |
| `ARIBA_DEFAULT_PAGE_SIZE` | No | `50` | Default page size |

---

## Project Structure

```
ariba-mcp/
├── src/ariba_mcp/
│   ├── server.py                      # FastMCP entrypoint
│   ├── config.py                      # Pydantic settings (reads .env)
│   ├── auth.py                        # OAuth 2.0 client credentials
│   ├── client.py                      # Async HTTP client (views, jobs, resources)
│   ├── errors.py                      # Error handling
│   ├── models/common.py              # Shared Pydantic models
│   └── tools/
│       ├── __init__.py                # Registers all 8 domains
│       ├── operational_procurement.py # Member 1
│       ├── operational_sourcing.py    # Member 2
│       ├── analytical_reporting.py    # Member 3
│       ├── supplier_data.py           # Member 4
│       ├── contract_compliance.py     # Member 5
│       ├── sourcing_project.py        # Member 6
│       ├── document_approval.py       # Member 7
│       └── supplier_risk.py           # Member 8
├── tests/
├── .agents/skills/mcp-builder/       # MCP builder reference docs
├── pyproject.toml
├── .env.example
├── CONTRIBUTING.md
└── .gitignore
```

---

## Team Assignment

| Member | Domain | Tool File | APIs Covered |
|--------|--------|-----------|-------------|
| 1 | Operational Procurement | `tools/operational_procurement.py` | Procurement Reporting (sync + async) |
| 2 | Operational Sourcing | `tools/operational_sourcing.py` | Sourcing Reporting views |
| 3 | Analytical Reporting | `tools/analytical_reporting.py` | Analytics (sync + async) |
| 4 | Supplier Data | `tools/supplier_data.py` | Supplier Data, Profiles, Qualifications |
| 5 | Contract Compliance | `tools/contract_compliance.py` | Contracts, Compliance, Terms |
| 6 | Sourcing Projects | `tools/sourcing_project.py` | Sourcing Projects, Approvals, Master Data |
| 7 | Approvals & Audit | `tools/document_approval.py` | Document Approval, Audit, Monitoring |
| 8 | Supplier Risk | `tools/supplier_risk.py` | Risk Exposure, Engagements, Categories |

**Shared infrastructure** (`config.py`, `auth.py`, `client.py`, `errors.py`, `server.py`) is maintained by the team collectively. Coordinate before making changes.

---

## How the APIs Work

### Authentication (OAuth 2.0)
```
POST https://api.ariba.com/v2/oauth/token?grant_type=client_credentials
Authorization: Basic {base64(client_id:client_secret)}
Content-Type: application/x-www-form-urlencoded
```
Returns `access_token` (expires in ~1440 seconds). The server handles this automatically.

### Reporting View Queries (sync)
```
GET https://openapi.ariba.com/api/{api-path}/views/{viewName}?realm={realm}&filters={json}
Authorization: Bearer {token}
apiKey: {api_key}
```
Returns records with optional `pageToken` for pagination.

### Async Jobs (for large datasets)
1. `POST .../jobs` → returns `jobId`
2. `GET .../jobs/{jobId}` → check status
3. `GET .../jobs/{jobId}` (with `pageToken`) → fetch results

### Resource APIs (sync)
```
GET https://openapi.ariba.com/api/{api-path}/{resource}?realm={realm}
```

---

## License

MIT
