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

    One team member registers the application on the SAP Ariba Developer Portal,
    then shares the .env file (or vault credentials) with the rest of the team.
    """

    # Required credentials — shared across all 8 team members
    ariba_realm: str
    ariba_client_id: str
    ariba_client_secret: str
    ariba_api_key: str

    # Base URLs (SAP Ariba standard endpoints)
    ariba_oauth_url: str = "https://api.ariba.com"
    ariba_api_url: str = "https://openapi.ariba.com/api"

    # Tuning
    request_timeout: int = 30
    default_page_size: int = 50
    max_page_size: int = 10000  # Ariba APIs support up to 10k per page for async

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> AribaSettings:
    """Return a singleton AribaSettings instance."""
    return AribaSettings()
