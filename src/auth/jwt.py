from typing import Any, Dict, Optional

import httpx
from fastapi import Header, HTTPException
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from jose.utils import base64url_decode

from src.config import get_settings


class JWKSCache:
    def __init__(self) -> None:
        self._jwks: Optional[Dict[str, Any]] = None
        self._uri: Optional[str] = None

    def get_jwks(self, uri: str) -> Dict[str, Any]:
        if self._jwks is None or self._uri != uri:
            response = httpx.get(uri, timeout=10.0)
            response.raise_for_status()
            self._jwks = response.json()
            self._uri = uri
        return self._jwks


jwks_cache = JWKSCache()


def _get_signing_key(token: str, jwks_uri: str) -> Dict[str, Any]:
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    if not kid:
        raise HTTPException(status_code=401, detail="token_missing_kid")

    jwks = jwks_cache.get_jwks(jwks_uri)
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    raise HTTPException(status_code=401, detail="signing_key_not_found")


def verify_token(authorization: str = Header(...)) -> Dict[str, Any]:
    settings = get_settings()
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing_bearer_token")
    token = authorization[7:]
    if not settings.OIDC_ISSUER or not settings.OIDC_JWKS_URI:
        raise HTTPException(status_code=500, detail="oidc_not_configured")

    key = _get_signing_key(token, settings.OIDC_JWKS_URI)

    try:
        claims = jwt.decode(
            token,
            key,
            algorithms=[key.get("alg", "RS256")],
            issuer=settings.OIDC_ISSUER,
            audience=settings.OIDC_AUDIENCE,
            options={"verify_at_hash": False},
        )
        return claims
    except ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="token_expired") from exc
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="invalid_token") from exc
