import uuid
from sqlalchemy import (
    String, Table, Column, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from app.database import Base

# --------------------------- RBAC tables --------------------------- #

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"),
           primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("role.id", ondelete="CASCADE"),
           primary_key=True),
)

class Role(Base):
    __tablename__ = "role"
    id   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)

# --------------------------- User table ---------------------------- #

class User(SQLAlchemyBaseUserTableUUID, Base):
    """User table extended with MFA secret and many-to-many roles."""
    mfa_secret = Column(String(length=32), nullable=True)

    roles = relationship(
        "Role",
        secondary=user_roles,
        backref="users",
        lazy="selectin",
    )

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role"""
        return role_name in {role.name for role in self.roles}

    @property
    def mfa_enabled(self) -> bool:
        """Check if multi-factor authentication is enabled"""
        return self.mfa_secret is not None