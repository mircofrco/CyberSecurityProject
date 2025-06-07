from fastapi import Depends, HTTPException, status
from typing import Callable
from app.api.auth.deps import current_active_user

def role_required(required: str) -> Callable:
    """
    FastAPI dependency generator – use:

        @router.get("/tally", dependencies=[Depends(role_required("election-admin"))])
    """
    async def _checker(user = Depends(current_active_user)):
        if required not in {r.name for r in user.roles}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required}' required",
            )
        return user  # user is returned for the endpoint if you need it
    return _checker
