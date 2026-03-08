from __future__ import annotations

from typing import Any, Dict, Optional

import boto3

from src.config import get_settings


class AWSAdapter:
    def __init__(self) -> None:
        settings = get_settings()
        self.region = settings.AWS_REGION
        self.sts = boto3.client("sts", region_name=self.region)
        self.tool_role_map = settings.TOOL_AWS_ROLE_MAP_JSON
        self.external_id = settings.TOOL_AWS_EXTERNAL_ID

    def _assume_role_for_tool(self, tool_name: str) -> boto3.Session:
        role_arn = self.tool_role_map.get(tool_name)
        if not role_arn:
            return boto3.Session(region_name=self.region)

        kwargs: Dict[str, Any] = {
            "RoleArn": role_arn,
            "RoleSessionName": f"mcp-{tool_name}",
        }
        if self.external_id:
            kwargs["ExternalId"] = self.external_id

        response = self.sts.assume_role(**kwargs)
        creds = response["Credentials"]
        return boto3.Session(
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
            region_name=self.region,
        )

    def list_guardduty_findings(self, detector_id: str, max_results: int = 20) -> Dict[str, Any]:
        session = self._assume_role_for_tool("aws_list_guardduty_findings")
        client = session.client("guardduty", region_name=self.region)
        finding_ids = client.list_findings(DetectorId=detector_id, MaxResults=max_results).get("FindingIds", [])
        if not finding_ids:
            return {"finding_ids": [], "findings": []}
        findings = client.get_findings(DetectorId=detector_id, FindingIds=finding_ids).get("Findings", [])
        return {"finding_ids": finding_ids, "findings": findings}

    def lookup_cloudtrail_events(
        self,
        lookup_attribute_key: str,
        lookup_attribute_value: str,
        max_results: int = 20,
    ) -> Dict[str, Any]:
        session = self._assume_role_for_tool("aws_lookup_cloudtrail_events")
        client = session.client("cloudtrail", region_name=self.region)
        events = client.lookup_events(
            LookupAttributes=[{"AttributeKey": lookup_attribute_key, "AttributeValue": lookup_attribute_value}],
            MaxResults=max_results,
        ).get("Events", [])
        return {"events": events}

    def list_securityhub_findings(self, max_results: int = 20, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        session = self._assume_role_for_tool("aws_get_securityhub_findings")
        client = session.client("securityhub", region_name=self.region)
        findings = client.get_findings(MaxResults=max_results, Filters=filters or {}).get("Findings", [])
        return {"findings": findings}
