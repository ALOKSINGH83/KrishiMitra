from dataclasses import dataclass
from typing import Any

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: str
    claims: dict[str, Any]


_jwks_cache: dict[str, Any] | None = None


async def _get_jwks() -> dict[str, Any]:
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache
    if not settings.supabase_jwks_url:
        raise HTTPException(status_code=503, detail="Authentication is not configured")
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(settings.supabase_jwks_url)
        response.raise_for_status()
        _jwks_cache = response.json()
        return _jwks_cache


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        jwks = await _get_jwks()
        header = jwt.get_unverified_header(credentials.credentials)
        key = next((item for item in jwks.get("keys", []) if item.get("kid") == header.get("kid")), None)
        if not key:
            raise JWTError("Signing key not found")
        claims = jwt.decode(
            credentials.credentials,
            key,
            algorithms=[header.get("alg", "RS256")],
            audience=settings.supabase_jwt_audience,
            issuer=settings.supabase_jwt_issuer or None,
        )
        subject = claims.get("sub")
        if not subject:
            raise JWTError("Missing subject")
        return CurrentUser(id=subject, claims=claims)
    except (JWTError, ValueError, httpx.HTTPError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
