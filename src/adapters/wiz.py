from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from src.adapters.secrets import get_secrets_adapter
from src.config import get_settings


class WizAdapter:
    def __init__(self) -> None:
        settings = get_settings()
        secrets = get_secrets_adapter()
        self.api_url = secrets.get_secret(settings.WIZ_API_URL_SECRET_NAME) if settings.WIZ_API_URL_SECRET_NAME else ""
        self.client_id = secrets.get_secret(settings.WIZ_CLIENT_ID_SECRET_NAME) if settings.WIZ_CLIENT_ID_SECRET_NAME else ""
        self.client_secret = secrets.get_secret(settings.WIZ_CLIENT_SECRET_SECRET_NAME) if settings.WIZ_CLIENT_SECRET_SECRET_NAME else ""
        self._token: Optional[str] = None

    def _get_token(self) -> str:
        if self._token:
            return self._token
        response = httpx.post(
            f"{self.api_url}/oauth/token",
            json={"client_id": self.client_id, "client_secret": self.client_secret, "grant_type": "client_credentials", "audience": "wiz-api"},
            timeout=20.0,
        )
        response.raise_for_status()
        self._token = response.json()["access_token"]
        return self._token

    def list_critical_exposures(self, project: Optional[str] = None) -> Dict[str, Any]:
        query = {
            "query": "query Issues($project: String) { issues(filterBy: {severity: [CRITICAL], projectName: $project}) { nodes { id name severity status project { name } } } }",
            "variables": {"project": project},
        }
        response = httpx.post(
            f"{self.api_url}/graphql",
            headers={"Authorization": f"Bearer {self._get_token()}"},
            json=query,
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()
