import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class CandidateRead(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    party: Optional[str] = None

    class Config:
        from_attributes = True


class ElectionRead(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    is_active: bool
    is_voting_open: bool
    candidates: List[CandidateRead] = []

    class Config:
        from_attributes = True


class VoterStatusResponse(BaseModel):
    can_vote: bool
    has_voted: bool
    message: str


class VoteRequest(BaseModel):
    candidate_id: uuid.UUID
    mfa_code: str


class VoteResponse(BaseModel):
    success: bool
    message: str
    vote_id: Optional[uuid.UUID] = None


class ElectionResultsResponse(BaseModel):
    election: ElectionRead
    total_votes: int
    results: List[dict]  # [{"candidate": CandidateRead, "votes": int, "percentage": float}]
    voter_turnout: dict  # {"eligible": int, "voted": int, "percentage": float}


class VoteConfirmationRequest(BaseModel):
    """Request model for confirming vote with MFA"""
    candidate_id: uuid.UUID
    mfa_code: str