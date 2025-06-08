from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth.router import router as auth_router
from app.api.auth.mfa_router import router as mfa_router
from app.api.admin.router import router as admin_router
from app.api.voting.router import router as voting_router

app = FastAPI(title="SecureVote")

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(mfa_router)
app.include_router(admin_router)
app.include_router(voting_router)  # Add voting router


@app.on_event("startup")
async def on_startup():
    # Create DB tables once; replace with Alembic in prod
    from app.database import Base, engine
    # Import all models to ensure they're registered
    from app.api.auth.models import User, Role
    from app.api.voting.models import Election, Candidate, VoterList, Vote

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/ping")
async def ping():
    return {"pong": True}