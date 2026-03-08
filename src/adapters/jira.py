from __future__ import annotations

import base64
from typing import Any, Dict

import httpx

from src.adapters.secrets import get_secrets_adapter
from src.config import get_settings


class JiraAdapter:
    def __init__(self) -> None:
        settings = get_settings()
        secrets = get_secrets_adapter()
        self.base_url = secrets.get_secret(settings.JIRA_BASE_URL_SECRET_NAME) if settings.JIRA_BASE_URL_SECRET_NAME else ""
        self.email = secrets.get_secret(settings.JIRA_EMAIL_SECRET_NAME) if settings.JIRA_EMAIL_SECRET_NAME else ""
        self.api_token = secrets.get_secret(settings.JIRA_API_TOKEN_SECRET_NAME) if settings.JIRA_API_TOKEN_SECRET_NAME else ""
        self.project_key = secrets.get_secret(settings.JIRA_PROJECT_KEY_SECRET_NAME) if settings.JIRA_PROJECT_KEY_SECRET_NAME else "SEC"

    def _headers(self) -> Dict[str, str]:
        token = base64.b64encode(f"{self.email}:{self.api_token}".encode("utf-8")).decode("utf-8")
        return {
            "Authorization": f"Basic {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def create_incident(self, summary: str, description: str, severity: str = "Medium") -> Dict[str, Any]:
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": "Task"},
                "labels": ["mcp", f"severity-{severity.lower()}"]
            }
        }
        response = httpx.post(f"{self.base_url}/rest/api/3/issue", headers=self._headers(), json=payload, timeout=20.0)
        response.raise_for_status()
        return response.json()

    def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        payload = {"body": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}]}}
        response = httpx.post(
            f"{self.base_url}/rest/api/3/issue/{issue_key}/comment",
            headers=self._headers(),
            json=payload,
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()
