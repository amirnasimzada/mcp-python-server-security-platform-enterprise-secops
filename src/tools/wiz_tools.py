from typing import Any, Dict, Optional

from src.adapters.wiz import WizAdapter


def wiz_list_critical_exposures(project: Optional[str] = None) -> Dict[str, Any]:
    return WizAdapter().list_critical_exposures(project=project)
