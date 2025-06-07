import uuid, os
from fastapi import Depends
from fastapi_users import FastAPIUsers, UUIDIDMixin
from fastapi_users.manager import BaseUserManager
from fastapi_users.authentication import (
    JWTStrategy, CookieTransport, AuthenticationBackend, BearerTransport
)
from fastapi_users.password import PasswordHelper
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.api.auth.models import User

RESET_TOKEN_SECRET = os.getenv("RESET_SECRET", "RESET_ME")
JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME")

password_helper = PasswordHelper()

# ------------------------------------------------------------------ #
# UserManager – simplified, no email verification                    #
# ------------------------------------------------------------------ #

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = RESET_TOKEN_SECRET

    async def on_after_register(self, user: User, request=None):
        # Optionally log registration or send a welcome email
        pass

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        # Optionally send "reset password" email
        pass


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

# ------------------------------------------------------------------ #
# Auth backend – JWT (header) + optional cookie                      #
# ------------------------------------------------------------------ #

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=JWT_SECRET, lifetime_seconds=3600)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
cookie_transport = CookieTransport(cookie_name="token", cookie_max_age=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)

