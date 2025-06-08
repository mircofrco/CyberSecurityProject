from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import pyotp

from app.database import get_async_session
from app.api.auth.deps import current_active_user
from app.api.auth.models import User
from app.api.voting.models import Election, Candidate, VoterList, Vote
from app.api.voting.schemas import (
    ElectionRead, VoterStatusResponse, VoteRequest, VoteResponse,
    ElectionResultsResponse, VoteConfirmationRequest
)
from app.api.crypto.paillier_utils import encrypt_ballot, generate_keypair

router = APIRouter(prefix="/voting", tags=["voting"])


@router.get("/elections", response_model=List[ElectionRead])
async def list_elections(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    """Get list of all active elections"""
    query = select(Election).where(Election.is_active == True)
    result = await session.execute(query)
    elections = result.scalars().all()

    # Load candidates for each election
    for election in elections:
        candidates_query = select(Candidate).where(Candidate.election_id == election.id)
        candidates_result = await session.execute(candidates_query)
        election.candidates = candidates_result.scalars().all()

    return elections


@router.get("/elections/{election_id}/status", response_model=VoterStatusResponse)
async def get_voter_status(
        election_id: str,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    """Check if user can vote in this election and if they have already voted"""

    # Check if election exists and is active
    election_query = select(Election).where(Election.id == election_id)
    election_result = await session.execute(election_query)
    election = election_result.scalar_one_or_none()

    if not election:
        raise HTTPException(status_code=404, detail="Election not found")

    if not election.is_voting_open:
        return VoterStatusResponse(
            can_vote=False,
            has_voted=False,
            message="Voting is not currently open for this election"
        )

    # Check if user is in voter list
    voter_query = select(VoterList).where(
        VoterList.election_id == election_id,
        VoterList.email == user.email
    )
    voter_result = await session.execute(voter_query)
    voter_entry = voter_result.scalar_one_or_none()

    if not voter_entry:
        return VoterStatusResponse(
            can_vote=False,
            has_voted=False,
            message="You are not eligible to vote in this election"
        )

    # Check if user has already voted
    vote_query = select(Vote).where(
        Vote.user_id == user.id,
        Vote.election_id == election_id
    )
    vote_result = await session.execute(vote_query)
    existing_vote = vote_result.scalar_one_or_none()

    if existing_vote:
        return VoterStatusResponse(
            can_vote=False,
            has_voted=True,
            message="You have already voted in this election"
        )

    # Check if user has MFA enabled
    if not user.mfa_enabled:
        return VoterStatusResponse(
            can_vote=False,
            has_voted=False,
            message="You must enable two-factor authentication before voting"
        )

    return VoterStatusResponse(
        can_vote=True,
        has_voted=False,
        message="You are eligible to vote in this election"
    )


@router.post("/elections/{election_id}/vote", response_model=VoteResponse)
async def cast_vote(
        election_id: str,
        vote_request: VoteConfirmationRequest,
        request: Request,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    """Cast a vote in an election (requires MFA verification)"""

    # Verify MFA first
    if not user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not enabled"
        )

    if not pyotp.TOTP(user.mfa_secret).verify(vote_request.mfa_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )

    # Check voter status
    voter_status = await get_voter_status(election_id, session, user)
    if not voter_status.can_vote:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=voter_status.message
        )

    # Verify candidate exists in this election
    candidate_query = select(Candidate).where(
        Candidate.id == vote_request.candidate_id,
        Candidate.election_id == election_id
    )
    candidate_result = await session.execute(candidate_query)
    candidate = candidate_result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found in this election"
        )

    # Create encrypted vote (for demo, we'll use simple encryption)
    # In production, you'd use the Paillier cryptosystem
    try:
        # For simplicity, we'll encrypt the value "1" (representing one vote)
        # In a real system, you'd use proper homomorphic encryption
        pub_key, priv_key = generate_keypair()
        encrypted_vote_data = encrypt_ballot(1, pub_key)

        # Create vote record
        vote = Vote(
            user_id=user.id,
            election_id=election_id,
            candidate_id=vote_request.candidate_id,
            encrypted_vote=encrypted_vote_data,
            mfa_verified=True,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", "")[:500]
        )

        session.add(vote)
        await session.commit()
        await session.refresh(vote)

        return VoteResponse(
            success=True,
            message=f"Vote successfully cast for {candidate.name}",
            vote_id=vote.id
        )

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cast vote. Please try again."
        )


@router.get("/elections/{election_id}/results", response_model=ElectionResultsResponse)
async def get_election_results(
        election_id: str,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    """Get election results (admin only or after election ends)"""

    # Check if user has admin role
    if not user.has_role("election-admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only election administrators can view results"
        )

    # Get election
    election_query = select(Election).where(Election.id == election_id)
    election_result = await session.execute(election_query)
    election = election_result.scalar_one_or_none()

    if not election:
        raise HTTPException(status_code=404, detail="Election not found")

    # Get candidates
    candidates_query = select(Candidate).where(Candidate.election_id == election_id)
    candidates_result = await session.execute(candidates_query)
    candidates = candidates_result.scalars().all()

    # Count votes for each candidate
    results = []
    total_votes = 0

    for candidate in candidates:
        vote_count_query = select(func.count(Vote.id)).where(
            Vote.candidate_id == candidate.id,
            Vote.election_id == election_id
        )
        vote_count_result = await session.execute(vote_count_query)
        vote_count = vote_count_result.scalar() or 0
        total_votes += vote_count

        results.append({
            "candidate": candidate,
            "votes": vote_count,
            "percentage": 0.0  # Will calculate after we have total
        })

    # Calculate percentages
    for result in results:
        if total_votes > 0:
            result["percentage"] = (result["votes"] / total_votes) * 100

    # Get voter turnout
    eligible_voters_query = select(func.count(VoterList.id)).where(
        VoterList.election_id == election_id
    )
    eligible_result = await session.execute(eligible_voters_query)
    eligible_voters = eligible_result.scalar() or 0

    voted_count_query = select(func.count(Vote.id.distinct())).where(
        Vote.election_id == election_id
    )
    voted_result = await session.execute(voted_count_query)
    voted_count = voted_result.scalar() or 0

    turnout_percentage = (voted_count / eligible_voters * 100) if eligible_voters > 0 else 0

    return ElectionResultsResponse(
        election=election,
        total_votes=total_votes,
        results=results,
        voter_turnout={
            "eligible": eligible_voters,
            "voted": voted_count,
            "percentage": turnout_percentage
        }
    )