from fastapi import APIRouter
from app.api.auth.deps import fastapi_users, auth_backend
from app.api.auth.schemas import UserRead, UserCreate, UserUpdate

router = APIRouter(prefix="/auth", tags=["auth"])

# jwt / login
router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/jwt", tags=["auth"]
)

# register / verify / reset
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="", tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="", tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="", tags=["auth"],
)
