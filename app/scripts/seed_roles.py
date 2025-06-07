import asyncio, uuid
from sqlalchemy import select
from app.database import async_session, engine
from app.api.auth.models import Role, Base

DEFAULT_ROLES = ("voter", "election-admin", "auditor")

async def main():
    # ensure tables exist (dev); use Alembic in prod
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        existing = (await session.scalars(select(Role.name))).all()
        for name in DEFAULT_ROLES:
            if name not in existing:
                session.add(Role(id=uuid.uuid4(), name=name))
        await session.commit()

if __name__ == "__main__":
    asyncio.run(main())
