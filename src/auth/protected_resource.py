from fastapi import APIRouter

from src.config import get_settings

router = APIRouter()


@router.get("/.well-known/oauth-protected-resource")
def oauth_protected_resource() -> dict:
    settings = get_settings()
    return {
        "resource": settings.APP_NAME,
        "authorization_servers": [settings.OAUTH_AUTHORIZATION_SERVER] if settings.OAUTH_AUTHORIZATION_SERVER else [],
        "bearer_methods_supported": ["header"],
        "resource_documentation": "https://example.internal/docs/mcp-python-server",
    }
