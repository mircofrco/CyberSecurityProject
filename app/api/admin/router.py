from fastapi import APIRouter, Depends

from app.api.auth.role_deps import role_required

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/tally")
async def view_tally(user = Depends(role_required("election-admin"))):
    # TODO: replace with real tally logic
    return {"status": "This would show the encrypted tally"}
