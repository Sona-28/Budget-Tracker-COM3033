from fastapi import Header, HTTPException, status

def get_internal_user_id(
    x_user_id: int = Header(None, alias="X-User-Id")
):
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing internal user identity"
        )
    return x_user_id
