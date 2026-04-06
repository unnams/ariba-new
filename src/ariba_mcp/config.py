"""Configuration for SAP Ariba MCP Server.

Reads credentials and settings from environment variables or a .env file.
Credentials are shared across the team — one person provisions them on the
SAP Ariba Developer Portal and distributes the .env file.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class AribaSettings(BaseSettings):
    """SAP Ariba connection settings.

    Required credentials (obtain from https://developer.ariba.com):
    - ARIBA_REALM        : Your Ariba realm (e.g. "mycompany-T" for test)
    - ARIBA_CLIENT_ID    : OAuth 2.0 application client ID
    - ARIBA_CLIENT_SECRET: OAuth 2.0 application client secret
    - ARIBA_API_KEY      : Application key from the developer portal

    Optional per-API credentials for testing multiple Ariba APIs with separate
    application keys or client credentials:
    - PRODUCT_HIERARCHY_MANAGEMENT_CLIENT_ID
    - PRODUCT_HIERARCHY_MANAGEMENT_CLIENT_SECRET
    - PRODUCT_HIERARCHY_MANAGEMENT_API_KEY
    - PRODUCT_HIERARCHY_MANAGEMENT_BASIC_AUTH
    - CONTRACT_TERMS_MANAGEMENT_CLIENT_ID
    - CONTRACT_TERMS_MANAGEMENT_CLIENT_SECRET
    - CONTRACT_TERMS_MANAGEMENT_API_KEY
    - CONTRACT_TERMS_MANAGEMENT_BASIC_AUTH
    - ORDER_CHANGE_REQUESTS_SUPPLIER_CLIENT_ID
    - ORDER_CHANGE_REQUESTS_SUPPLIER_CLIENT_SECRET
    - ORDER_CHANGE_REQUESTS_SUPPLIER_API_KEY
    - ORDER_CHANGE_REQUESTS_SUPPLIER_BASIC_AUTH
    - SUPPLIER_INFORMATION_CLIENT_ID
    - SUPPLIER_INFORMATION_CLIENT_SECRET
    - SUPPLIER_INFORMATION_API_KEY
    - SUPPLIER_INFORMATION_BASIC_AUTH

    One team member registers the application on the SAP Ariba Developer Portal,
    then shares the .env file (or vault credentials) with the rest of the team.
    """

    # Required credentials — shared across all 8 team members
    ariba_realm: str
    ariba_client_id: str
    ariba_client_secret: str
    ariba_api_key: str

    # Supplier Risk Engagements API credentials
    ariba_risk_client_id: str = ""
    ariba_risk_client_secret: str = ""
    ariba_risk_api_key: str = ""

    # Supplier Data API (supplierdataaccess/v1) credentials
    ariba_sda_client_id: str = ""
    ariba_sda_client_secret: str = ""
    ariba_sda_api_key: str = ""

    # Supplier Invite API credentials
    ariba_invite_client_id: str = ""
    ariba_invite_client_secret: str = ""
    ariba_invite_api_key: str = ""

    # Supplier Data Pagination API credentials
    ariba_sdp_client_id: str = ""
    ariba_sdp_client_secret: str = ""
    ariba_sdp_api_key: str = ""

    # Sourcing Approval API credentials
    sourcing_approval_client_id: str = ""
    sourcing_approval_client_secret: str = ""
    sourcing_approval_api_key: str = ""

    # Integration Monitoring for Procurement API credentials
    integration_monitoring_client_id: str = ""
    integration_monitoring_client_secret: str = ""
    integration_monitoring_api_key: str = ""

    # Pranathi APIs (Master Data, Pricing, Sourcing Event Status)
    pranathi_client_id: str = ""
    pranathi_client_secret: str = ""
    pranathi_api_key: str = ""

    # Invoice API credentials
    invoice_ariba_client_id: str = ""
    invoice_ariba_client_secret: str = ""
    invoice_ariba_api_key: str = ""

    # Catalog Connectivity Service API credentials
    catalog_ariba_client_id: str = ""
    catalog_ariba_client_secret: str = ""
    catalog_ariba_api_key: str = ""

    # Data Replication Status credentials
    replication_ariba_client_id: str = ""
    replication_ariba_client_secret: str = ""
    replication_ariba_api_key: str = ""

    # Surrogate Bidding API credentials
    api_surrogate_bidding_client_id: str = ""
    api_surrogate_bidding_client_secret: str = ""
    api_surrogate_bidding_api_key: str = ""

    # Asset Management API credentials
    api_asset_management_client_id: str = ""
    api_asset_management_client_secret: str = ""
    api_asset_management_api_key: str = ""

    # Audit Search API credentials
    audit_search_client_id: str = ""
    audit_search_client_secret: str = ""
    audit_search_api_key: str = ""

    # Document Approval API credentials
    document_approval_client_id: str = ""
    document_approval_client_secret: str = ""
    document_approval_api_key: str = ""

    # Contract Compliance API credentials
    contract_compliance_client_id: str = ""
    contract_compliance_client_secret: str = ""
    contract_compliance_api_key: str = ""

    # Procurement Workspace API credentials
    procurement_workspace_client_id: str = ""
    procurement_workspace_client_secret: str = ""
    procurement_workspace_api_key: str = ""

    # Risk Category Information API credentials
    risk_category_information_client_id: str = ""
    risk_category_information_client_secret: str = ""
    risk_category_information_api_key: str = ""

    # Cost Breakdown API credentials
    cost_breakdown_client_id: str = ""
    cost_breakdown_client_secret: str = ""
    cost_breakdown_api_key: str = ""

    # Strategic Sourcing Event Status API URL (Pranathi)
    ariba_event_status_api: str = "https://openapi.ariba.com/api/strategicsourcing-eventstatus/v2/prod"

    # Optional per-API credentials (use when an API has its own application key)
    product_hierarchy_management_client_id: str | None = None
    product_hierarchy_management_client_secret: str | None = None
    product_hierarchy_management_api_key: str | None = None
    product_hierarchy_management_basic_auth: str | None = None
    contract_terms_management_client_id: str | None = None
    contract_terms_management_client_secret: str | None = None
    contract_terms_management_api_key: str | None = None
    contract_terms_management_basic_auth: str | None = None
    order_change_requests_supplier_client_id: str | None = None
    order_change_requests_supplier_client_secret: str | None = None
    order_change_requests_supplier_api_key: str | None = None
    order_change_requests_supplier_basic_auth: str | None = None
    supplier_information_client_id: str | None = None
    supplier_information_client_secret: str | None = None
    supplier_information_api_key: str | None = None
    supplier_information_basic_auth: str | None = None

    # Base URLs (SAP Ariba standard endpoints)
    ariba_oauth_url: str = "https://api.ariba.com"
    ariba_api_url: str = "https://openapi.ariba.com/api"

    def get_api_settings(self, api_name: str) -> "AribaSettings":
        api_name = api_name.lower()
        supported_api_names = {
            "product_hierarchy_management",
            "contract_terms_management",
            "order_change_requests_supplier",
            "supplier_information",
        }
        if api_name not in supported_api_names:
            return self

        update: dict[str, str] = {}
        credential_map = {
            "client_id": "ariba_client_id",
            "client_secret": "ariba_client_secret",
            "api_key": "ariba_api_key",
        }

        for source_suffix, target_field in credential_map.items():
            source_attr = f"{api_name}_{source_suffix}"
            value = getattr(self, source_attr, None)
            if value:
                update[target_field] = value

        return self.model_copy(update=update) if update else self
    ariba_network_id: str | None = None

    # Tuning
    request_timeout: int = 30
    default_page_size: int = 50
    max_page_size: int = 10000  # Ariba APIs support up to 10k per page for async

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> AribaSettings:
    """Return a singleton AribaSettings instance."""
    return AribaSettings()
