from typing import Any, Dict, Optional

from src.adapters.aws import AWSAdapter


def aws_list_guardduty_findings(detector_id: str, max_results: int = 20) -> Dict[str, Any]:
    return AWSAdapter().list_guardduty_findings(detector_id=detector_id, max_results=max_results)


def aws_lookup_cloudtrail_events(attribute_key: str, attribute_value: str, max_results: int = 20) -> Dict[str, Any]:
    return AWSAdapter().lookup_cloudtrail_events(
        lookup_attribute_key=attribute_key,
        lookup_attribute_value=attribute_value,
        max_results=max_results,
    )


def aws_get_securityhub_findings(max_results: int = 20, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return AWSAdapter().list_securityhub_findings(max_results=max_results, filters=filters)
