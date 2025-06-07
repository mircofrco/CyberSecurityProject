# quick-and-dirty example inside a Python REPL
import asyncio
from sqlalchemy import select
from app.database import async_session
from app.api.auth.models import User, Role

async def add_admin(email="alice@example.com"):
    async with async_session() as s:
        user = (await s.scalar(select(User).where(User.email == email)))
        admin_role = (await s.scalar(select(Role).where(Role.name == "election-admin")))
        user.roles.append(admin_role)
        await s.commit()
asyncio.run(add_admin())
