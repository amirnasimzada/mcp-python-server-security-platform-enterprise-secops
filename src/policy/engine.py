from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

import yaml
from fastapi import HTTPException

from src.config import get_settings


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str


class PolicyEngine:
    def __init__(self, policy_path: str) -> None:
        self.policy_path = Path(policy_path)
        self.policy = self._load_policy()

    def _load_policy(self) -> Dict[str, Any]:
        if not self.policy_path.exists():
            raise RuntimeError(f"Policy file not found: {self.policy_path}")
        return yaml.safe_load(self.policy_path.read_text()) or {}

    @staticmethod
    def _normalize_list(value: Any) -> Set[str]:
        if value is None:
            return set()
        if isinstance(value, str):
            return set(value.split())
        if isinstance(value, Iterable):
            return {str(v) for v in value}
        return set()

    def authorize(self, tool_name: str, claims: Dict[str, Any], action: str = "read") -> PolicyDecision:
        tools = self.policy.get("tools", {})
        rule = tools.get(tool_name)
        if not rule:
            return PolicyDecision(False, "tool_not_defined")

        allow = rule.get("allow", {})
        if allow.get("authenticated") and claims.get("sub"):
            pass

        required_scopes = set(allow.get("scopes", []))
        required_groups = set(allow.get("groups", []))
        required_tenants = set(allow.get("tenants", []))
        allowed_actions = set(rule.get("actions", [action]))

        scopes = self._normalize_list(claims.get("scp"))
        groups = self._normalize_list(claims.get("groups"))
        tenant = claims.get("tenant")

        if action not in allowed_actions:
            return PolicyDecision(False, "action_not_allowed")
        if required_scopes and not (required_scopes & scopes):
            return PolicyDecision(False, "missing_scope")
        if required_groups and not (required_groups & groups):
            return PolicyDecision(False, "missing_group")
        if required_tenants and tenant not in required_tenants:
            return PolicyDecision(False, "tenant_not_allowed")
        return PolicyDecision(True, "allowed")


_engine: PolicyEngine | None = None


def get_policy_engine() -> PolicyEngine:
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = PolicyEngine(settings.POLICY_FILE)
    return _engine


def enforce_policy(tool_name: str, claims: Dict[str, Any], action: str = "read") -> None:
    decision = get_policy_engine().authorize(tool_name, claims, action=action)
    if not decision.allowed:
        raise HTTPException(status_code=403, detail={"tool": tool_name, "reason": decision.reason})
