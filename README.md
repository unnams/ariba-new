# SAP Ariba MCP Server

A **Model Context Protocol (MCP) server** that exposes **48 SAP Ariba APIs** as Claude-compatible tools. Built with Python and [FastMCP](https://github.com/jlowin/fastmcp).

This enables Claude (or any MCP-compatible AI) to interact with SAP Ariba procurement, sourcing, supplier management, contracts, catalogs, and supply chain data via natural language.

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
│  │ 8 Domain │  │ Auth     │  │ Client   │       │
│  │ Modules  │──│ OAuth2.0 │──│ httpx    │       │
│  │ 48 APIs  │  │ cached   │  │ async    │       │
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

## All 48 APIs — Domain Modules & Owners

### 1. Supplier Management — [supplier_management.py](src/ariba_mcp/tools/supplier_management.py)

| API | Owner |
|-----|-------|
| Supplier Data API with Pagination | Nitish SM |
| Supplier Data API | Nitish SM |
| Supplier Data Extraction API | Nitish SM |
| Ariba Network Supplier Profile API | Nitish SM |
| Supplier Invite API | Nitish SM |
| Supplier Information API | Shabreen |
| Supplier Risk Engagements API | Nitish SM |
| Risk Exposure API | Anim |
| Risk Category Information API | Shabreen |

### 2. Procurement Reporting — [procurement_reporting.py](src/ariba_mcp/tools/procurement_reporting.py)

| API | Owner |
|-----|-------|
| Operational Reporting API for Procurement | Vanshika |
| Analytical Reporting API (Strategic & Operational Procurement) | Anim |

### 3. Sourcing — [sourcing.py](src/ariba_mcp/tools/sourcing.py)

| API | Owner |
|-----|-------|
| Operational Reporting API for Strategic Sourcing | Pranathi |
| Sourcing Project Management API | Pranathi |
| Event Management API | Anim |
| External Approval API for Sourcing & Supplier Mgmt | Pranathi |
| Master Data Retrieval API for Sourcing | Pranathi |
| Pricing API for Product Sourcing | Pranathi |
| Surrogate Bid API | Rohit Naik |
| Product Hierarchy Management API | Shabreen |
| Bill of Materials Import API | Anim |

### 4. Contracts — [contracts.py](src/ariba_mcp/tools/contracts.py)

| API | Owner |
|-----|-------|
| Contract Compliance API | Vanshika |
| Contract Workspace Retrieval API | Anim |
| Contract Workspace Management APIs | Rohit Naik |
| Contract Terms Management API | Shabreen |
| NDA Data Export API | Rohit Naik |
| Cost Breakdown Data Extraction API | Vanshika |

### 5. Purchase Orders — [purchase_orders.py](src/ariba_mcp/tools/purchase_orders.py)

| API | Owner |
|-----|-------|
| Purchase Orders Supplier API | Nitish SM |
| Ariba Network Purchase Orders API | Anil |
| Order Change Requests API for Buyers | Anim |
| Order Change Requests API for Suppliers | Shabreen |

### 6. Catalogs — [catalogs.py](src/ariba_mcp/tools/catalogs.py)

| API | Owner |
|-----|-------|
| Internal Catalogs Shop API | Anil |
| Public Catalogs Shop API | Anil |
| Network Catalog Management API | Anil |
| SAP Ariba Catalog Content API | Ayub |
| Catalog Connectivity Service API | Ayub |
| Content Lookup API | Anil |
| Materials and BOM Tag Management API | Anil |

### 7. Supply Chain & Network — [supply_chain.py](src/ariba_mcp/tools/supply_chain.py)

| API | Owner |
|-----|-------|
| Ship Notice API for Buyers | Ayub |
| Ship Notice API for Suppliers | Shabreen |
| Planning Collaboration Buyer API | Anim |
| Planning Collaboration Supplier API | Shabreen |
| Proof of Service API for Buyers | (unassigned) |
| Ariba Network Invoice Header Data Extraction API | Ayub |
| Trading Partner Profile Certification API | Ayub |
| Data Replication Status for Multi-ERP | Ayub |

### 8. Administration & Monitoring — [administration.py](src/ariba_mcp/tools/administration.py)

| API | Owner |
|-----|-------|
| Document Approval API | Anim |
| Audit Search API | Vanshika |
| Integration Monitoring API for Procurement | Vanshika |
| Integration Monitoring API for Strategic Sourcing | Pranathi |
| Transaction Monitoring API | Anim |
| Master Data Integration Job Status API | Anim |
| Configuration Parameter Review API | Vanshika |
| SAP Ariba Custom Forms API | Vanshika |
| Asset Management API | Rohit Naik |
| Master Data Retrieval API for Procurement | Rohit Naik |
| Guided Buying Functional Documents API | Anim |
| Create Procurement Workspace API | Vanshika |
| User Qualification API | Anil |
| Public Procurement Notices Export API | Rohit Naik |

---

## Prerequisites

- **Python 3.11+**
- **uv** (recommended) or pip
- **SAP Ariba API credentials** — one person provisions them for the team

---

## Credential Setup (One-time)

One team member registers on the SAP Ariba Developer Portal and shares credentials:

1. Go to https://developer.ariba.com
2. Register a new application
3. Enable the APIs needed
4. Note: **OAuth Client ID**, **Client Secret**, **API Key**, **Realm** name
5. Create `.env` and share securely:

```bash
cp .env.example .env
# Fill in credentials
```

> **Never commit `.env` to git.**

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/nitishsm2002/ariba-mcp.git
cd ariba-mcp
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Add .env file (get from credentials owner)

# Run the server
python -m ariba_mcp.server

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python -m ariba_mcp.server
```

### Connect to Claude Desktop

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

---

## Project Structure

```
ariba-mcp/
├── src/ariba_mcp/
│   ├── server.py                   # FastMCP entrypoint
│   ├── config.py                   # Settings (reads .env)
│   ├── auth.py                     # OAuth 2.0 client credentials
│   ├── client.py                   # Async HTTP client (views, jobs, resources)
│   ├── errors.py                   # Error handling
│   ├── models/common.py           # Shared Pydantic models
│   └── tools/
│       ├── __init__.py             # Registers all 8 domains
│       ├── supplier_management.py  # 9 APIs — Supplier data, risk, profiles
│       ├── procurement_reporting.py # 2 APIs — Operational + Analytical reporting
│       ├── sourcing.py             # 9 APIs — Sourcing projects, events, approvals
│       ├── contracts.py            # 6 APIs — Compliance, workspaces, terms, NDA
│       ├── purchase_orders.py      # 4 APIs — PO buyer/supplier, order changes
│       ├── catalogs.py             # 7 APIs — Internal/public/network catalogs
│       ├── supply_chain.py         # 8 APIs — Ship notice, planning, invoices
│       └── administration.py       # 14 APIs — Approvals, audit, monitoring, config
├── tests/
├── .agents/skills/mcp-builder/    # MCP builder reference docs
├── pyproject.toml
├── .env.example
├── CONTRIBUTING.md
└── .gitignore
```

---

## How to Implement Your API

Each tool file has **one working example** and **TODO comments** for the rest. To implement your API:

1. Open your domain file in `src/ariba_mcp/tools/`
2. Find your API in the TODO list
3. Check the API docs link in the file header
4. Look up the exact endpoint path on the [Developer Portal](https://developer.ariba.com)
5. Add the API path constant at the top of the file
6. Copy the example tool pattern and implement your tool
7. Test with MCP Inspector

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed coding patterns.

---

## Configuration Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ARIBA_REALM` | Yes | — | Ariba realm (e.g. `mycompany-T`) |
| `ARIBA_CLIENT_ID` | Yes | — | OAuth 2.0 client ID |
| `ARIBA_CLIENT_SECRET` | Yes | — | OAuth 2.0 client secret |
| `ARIBA_API_KEY` | Yes | — | Application key |
| `ARIBA_OAUTH_URL` | No | `https://api.ariba.com` | OAuth endpoint |
| `ARIBA_API_URL` | No | `https://openapi.ariba.com/api` | API base URL |

---

## License

MIT
