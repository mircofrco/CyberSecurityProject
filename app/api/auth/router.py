from fastapi import APIRouter, Depends
from app.api.auth.deps import fastapi_users, auth_backend, current_active_user
from app.api.auth.schemas import UserRead, UserCreate
from app.api.auth.models import User

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


# Custom /users/me endpoint with proper MFA status
@router.get("/users/me", response_model=UserRead, tags=["users"])
async def get_current_user_info(user: User = Depends(current_active_user)):
    """
    Get current authenticated user information with the correct MFA status.

    Returns:
        UserRead: Current user data including computed mfa_enabled status
    """
    # Convert a User model to UserRead schema with computed mfa_enabled
    return UserRead(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        is_verified=user.is_verified,
        mfa_enabled=user.mfa_secret is not None  # Compute MFA status
    )

