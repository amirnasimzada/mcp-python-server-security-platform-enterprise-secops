from typing import Any, Dict

from src.adapters.jira import JiraAdapter


def jira_create_incident(summary: str, description: str, severity: str = "Medium") -> Dict[str, Any]:
    return JiraAdapter().create_incident(summary=summary, description=description, severity=severity)


def jira_add_comment(issue_key: str, comment: str) -> Dict[str, Any]:
    return JiraAdapter().add_comment(issue_key=issue_key, comment=comment)
