import asyncio, uuid
from sqlalchemy import select
from app.database import async_session, engine
from app.api.auth.models import Role, Base

DEFAULT_ROLES = ("voter", "election-admin", "auditor")

async def main():
    # ensure tables exist (dev); use Alembic in prod
    print("Creating database tables (if they do not exist)...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables ensured.")

    async with async_session() as session:
        print("Checking for existing roles in the database...")
        existing = (await session.scalars(select(Role.name))).all()
        print(f"Found existing roles: {existing}")

        added_roles = []
        for name in DEFAULT_ROLES:
            if name not in existing:
                session.add(Role(id=uuid.uuid4(), name=name))
                added_roles.append(name)

        if added_roles:
            await session.commit()
            print(f"✅ Added missing roles: {added_roles}")
        else:
            print("✅ No new roles needed. All default roles already exist.")

if __name__ == "__main__":
    asyncio.run(main())
