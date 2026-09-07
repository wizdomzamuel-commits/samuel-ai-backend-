"""
Minimal API key auth suitable for a single-user personal assistant.

Clients must send: X-API-Key: <your key>
"""

from fastapi import Header, HTTPException, status

from app.core.config import get_settings

settings = get_settings()


def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> None:
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
