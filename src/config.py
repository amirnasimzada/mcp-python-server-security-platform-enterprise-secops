import json
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "mcp-python-server")
    APP_VERSION: str = os.getenv("APP_VERSION", "2.0.0")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    OIDC_ISSUER: str = os.getenv("OIDC_ISSUER", "")
    OIDC_AUDIENCE: str = os.getenv("OIDC_AUDIENCE", "mcp-server")
    OIDC_JWKS_URI: str = os.getenv("OIDC_JWKS_URI", "")
    OAUTH_AUTHORIZATION_SERVER: str = os.getenv("OAUTH_AUTHORIZATION_SERVER", "")

    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    POLICY_FILE: str = os.getenv("POLICY_FILE", "src/policy/rules.yaml")
    AUDIT_LOG_PATH: str = os.getenv("AUDIT_LOG_PATH", "")

    JIRA_BASE_URL_SECRET_NAME: str = os.getenv("JIRA_BASE_URL_SECRET_NAME", "")
    JIRA_EMAIL_SECRET_NAME: str = os.getenv("JIRA_EMAIL_SECRET_NAME", "")
    JIRA_API_TOKEN_SECRET_NAME: str = os.getenv("JIRA_API_TOKEN_SECRET_NAME", "")
    JIRA_PROJECT_KEY_SECRET_NAME: str = os.getenv("JIRA_PROJECT_KEY_SECRET_NAME", "")

    WIZ_API_URL_SECRET_NAME: str = os.getenv("WIZ_API_URL_SECRET_NAME", "")
    WIZ_CLIENT_ID_SECRET_NAME: str = os.getenv("WIZ_CLIENT_ID_SECRET_NAME", "")
    WIZ_CLIENT_SECRET_SECRET_NAME: str = os.getenv("WIZ_CLIENT_SECRET_SECRET_NAME", "")

    TOOL_AWS_ROLE_MAP_JSON: Dict[str, str] = json.loads(os.getenv("TOOL_AWS_ROLE_MAP_JSON", "{}"))
    TOOL_AWS_EXTERNAL_ID: Optional[str] = os.getenv("TOOL_AWS_EXTERNAL_ID")

    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    MAX_RESULTS_DEFAULT: int = int(os.getenv("MAX_RESULTS_DEFAULT", "20"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
