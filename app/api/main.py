from fastapi import FastAPI

from app.api.auth.router import router as auth_router
from app.api.auth.mfa_router import router as mfa_router
from app.api.admin.router import router as admin_router

app = FastAPI(title="SecureVote")

app.include_router(auth_router)
app.include_router(mfa_router)
app.include_router(admin_router)


@app.on_event("startup")
async def on_startup():
    # create DB tables once;
    from app.database import Base, engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/ping")
async def ping():
    return {"pong": True}
