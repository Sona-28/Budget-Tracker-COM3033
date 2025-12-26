import os
import requests
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer(auto_error=False)

AUTH_VERIFY_ENDPOINT = os.getenv(
    "AUTH_VERIFY_ENDPOINT",
    "http://localhost:5001/verify"
)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id")
):
    """
    Auth priority:
    1. JWT token (Authorization: Bearer <token>)
    2. Internal trusted call (X-User-Id header)
    """

    # ---------- JWT-based auth ----------
    if credentials:
        token = credentials.credentials

        try:
            response = requests.get(
                AUTH_VERIFY_ENDPOINT,
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
        except requests.RequestException:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth service unavailable"
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        return response.json()  # must include user_id

    # ---------- Internal service auth ----------
    if x_user_id is not None:
        return {"user_id": int(x_user_id)}

    # ---------- No auth ----------
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated"
    )
