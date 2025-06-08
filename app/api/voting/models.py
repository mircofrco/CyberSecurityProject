import uuid
from datetime import datetime
from sqlalchemy import (
    String, Text, DateTime, Boolean, Integer, ForeignKey, UniqueConstraint, Column
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

# Import User model to ensure table is registered
from app.api.auth.models import User


class Election(Base):
    """Election model - represents a voting election"""
    __tablename__ = "election"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    candidates = relationship("Candidate", back_populates="election", cascade="all, delete-orphan")
    voter_list = relationship("VoterList", back_populates="election", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="election", cascade="all, delete-orphan")

    @property
    def is_voting_open(self) -> bool:
        """Check if voting is currently open"""
        now = datetime.utcnow()
        return self.is_active and self.start_date <= now <= self.end_date


class Candidate(Base):
    """Candidate model - represents a candidate in an election"""
    __tablename__ = "candidate"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    party = Column(String(100), nullable=True)
    election_id = Column(UUID(as_uuid=True), ForeignKey("election.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    election = relationship("Election", back_populates="candidates")
    votes = relationship("Vote", back_populates="candidate")


class VoterList(Base):
    """VoterList model - predefined list of eligible voters for each election"""
    __tablename__ = "voter_list"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False)
    election_id = Column(UUID(as_uuid=True), ForeignKey("election.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    election = relationship("Election", back_populates="voter_list")

    # Ensure one entry per email per election
    __table_args__ = (UniqueConstraint('email', 'election_id', name='unique_voter_per_election'),)


class Vote(Base):
    """Vote model - represents a cast vote (encrypted for privacy)"""
    __tablename__ = "vote"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    election_id = Column(UUID(as_uuid=True), ForeignKey("election.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidate.id", ondelete="CASCADE"), nullable=False)

    # Encrypted vote for privacy (using Paillier homomorphic encryption)
    encrypted_vote = Column(Text, nullable=False)  # Base64 encoded encrypted vote

    # Security and audit fields
    mfa_verified = Column(Boolean, default=False, nullable=False)
    ip_address = Column(String(45), nullable=True)  # For audit trail
    user_agent = Column(String(500), nullable=True)  # For audit trail
    cast_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User")
    election = relationship("Election", back_populates="votes")
    candidate = relationship("Candidate", back_populates="votes")

    # Ensure one vote per user per election
    __table_args__ = (UniqueConstraint('user_id', 'election_id', name='one_vote_per_user_per_election'),)