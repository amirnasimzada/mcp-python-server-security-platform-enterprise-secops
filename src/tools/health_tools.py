from typing import Any, Dict


def healthcheck() -> Dict[str, Any]:
    return {"ok": True}
