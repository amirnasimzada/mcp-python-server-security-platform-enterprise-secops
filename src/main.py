from __future__ import annotations

from typing import Any, Dict, Optional

import uvicorn
from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel, Field

from src.audit.logger import audit_event
from src.auth.jwt import verify_token
from src.auth.protected_resource import router as protected_resource_router
from src.config import get_settings
from src.policy.engine import enforce_policy
from src.tools.aws_tools import (
    aws_get_securityhub_findings,
    aws_list_guardduty_findings,
    aws_lookup_cloudtrail_events,
)
from src.tools.health_tools import healthcheck
from src.tools.jira_tools import jira_add_comment, jira_create_incident
from src.tools.wiz_tools import wiz_list_critical_exposures

app = FastAPI(title="mcp-python-server", version="2.0.0")
app.include_router(protected_resource_router)


class GuardDutyRequest(BaseModel):
    detector_id: str
    max_results: int = Field(default=20, le=100)


class CloudTrailRequest(BaseModel):
    attribute_key: str
    attribute_value: str
    max_results: int = Field(default=20, le=50)


class SecurityHubRequest(BaseModel):
    max_results: int = Field(default=20, le=100)
    filters: Optional[Dict[str, Any]] = None


class JiraIncidentRequest(BaseModel):
    summary: str
    description: str
    severity: str = "Medium"


class JiraCommentRequest(BaseModel):
    issue_key: str
    comment: str


class WizRequest(BaseModel):
    project: Optional[str] = None


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    response = await call_next(request)
    return response


@app.get("/healthz")
def healthz() -> Dict[str, Any]:
    return healthcheck()


@app.post("/mcp/tools/aws_list_guardduty_findings")
def route_aws_list_guardduty_findings(body: GuardDutyRequest, claims: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    tool_name = "aws_list_guardduty_findings"
    enforce_policy(tool_name, claims, action="read")
    result = aws_list_guardduty_findings(detector_id=body.detector_id, max_results=body.max_results)
    audit_event("tool_invocation", {"tool": tool_name, "subject": claims.get("sub"), "status": "success"})
    return result


@app.post("/mcp/tools/aws_lookup_cloudtrail_events")
def route_aws_lookup_cloudtrail_events(body: CloudTrailRequest, claims: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    tool_name = "aws_lookup_cloudtrail_events"
    enforce_policy(tool_name, claims, action="read")
    result = aws_lookup_cloudtrail_events(body.attribute_key, body.attribute_value, body.max_results)
    audit_event("tool_invocation", {"tool": tool_name, "subject": claims.get("sub"), "status": "success"})
    return result


@app.post("/mcp/tools/aws_get_securityhub_findings")
def route_aws_get_securityhub_findings(body: SecurityHubRequest, claims: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    tool_name = "aws_get_securityhub_findings"
    enforce_policy(tool_name, claims, action="read")
    result = aws_get_securityhub_findings(max_results=body.max_results, filters=body.filters)
    audit_event("tool_invocation", {"tool": tool_name, "subject": claims.get("sub"), "status": "success"})
    return result


@app.post("/mcp/tools/jira_create_incident")
def route_jira_create_incident(body: JiraIncidentRequest, claims: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    tool_name = "jira_create_incident"
    enforce_policy(tool_name, claims, action="write")
    result = jira_create_incident(summary=body.summary, description=body.description, severity=body.severity)
    audit_event("tool_invocation", {"tool": tool_name, "subject": claims.get("sub"), "status": "success", "jira_key": result.get("key")})
    return result


@app.post("/mcp/tools/jira_add_comment")
def route_jira_add_comment(body: JiraCommentRequest, claims: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    tool_name = "jira_add_comment"
    enforce_policy(tool_name, claims, action="write")
    result = jira_add_comment(issue_key=body.issue_key, comment=body.comment)
    audit_event("tool_invocation", {"tool": tool_name, "subject": claims.get("sub"), "status": "success", "jira_key": body.issue_key})
    return result


@app.post("/mcp/tools/wiz_list_critical_exposures")
def route_wiz_list_critical_exposures(body: WizRequest, claims: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    tool_name = "wiz_list_critical_exposures"
    enforce_policy(tool_name, claims, action="read")
    result = wiz_list_critical_exposures(project=body.project)
    audit_event("tool_invocation", {"tool": tool_name, "subject": claims.get("sub"), "status": "success"})
    return result


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=False)
