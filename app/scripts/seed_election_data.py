import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy import select
from app.database import async_session, engine
from app.database import Base

# Import ALL models to ensure they're registered with SQLAlchemy
from app.api.auth.models import User, Role
from app.api.voting.models import Election, Candidate, VoterList, Vote


async def seed_election_data():
    """Seed database with example election and voter data"""

    # Ensure all tables exist
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created!")

    async with async_session() as session:
        # Check if election already exists
        existing_election = await session.execute(
            select(Election).where(Election.title == "2024 Student Council Election")
        )
        if existing_election.scalar_one_or_none():
            print("❗ Election data already exists. Skipping seed.")
            return

        print("Creating election data...")

        # Create example election
        election = Election(
            id=uuid.uuid4(),
            title="2024 Student Council Election",
            description="Annual student council election to select the next student body president.",
            start_date=datetime.utcnow() - timedelta(days=1),  # Started yesterday
            end_date=datetime.utcnow() + timedelta(days=7),  # Ends in 7 days
            is_active=True
        )
        session.add(election)
        await session.flush()  # Get the election ID

        # Create candidates
        candidates = [
            Candidate(
                id=uuid.uuid4(),
                name="Alice Johnson",
                description="Experienced leader with a vision for student engagement and campus improvements.",
                party="Progressive Student Alliance",
                election_id=election.id
            ),
            Candidate(
                id=uuid.uuid4(),
                name="Bob Martinez",
                description="Advocate for academic excellence and student welfare programs.",
                party="Academic Excellence Party",
                election_id=election.id
            ),
            Candidate(
                id=uuid.uuid4(),
                name="Carol Kim",
                description="Committed to sustainability, diversity, and inclusive campus policies.",
                party="Green Future Coalition",
                election_id=election.id
            )
        ]

        for candidate in candidates:
            session.add(candidate)

        # Create voter list (predefined eligible voters)
        eligible_voters = [
            "alice@example.com",
            "bob@example.com",
            "carol@example.com",
            "admin@example.com",
            "voter1@student.edu",
            "voter2@student.edu",
            "voter3@student.edu",
            "voter4@student.edu",
            "voter5@student.edu",
            "test@example.com"
        ]

        for email in eligible_voters:
            voter_entry = VoterList(
                id=uuid.uuid4(),
                email=email,
                election_id=election.id
            )
            session.add(voter_entry)

        await session.commit()

        print("✅ Election data seeded successfully!")
        print(f"📊 Election: {election.title}")
        print(f"🗳️  Candidates: {len(candidates)}")
        print(f"👥 Eligible voters: {len(eligible_voters)}")
        print(f"⏰ Voting period: {election.start_date} to {election.end_date}")
        print()
        print("Eligible voter emails:")
        for email in eligible_voters:
            print(f"  - {email}")


async def create_more_elections():
    """Create additional elections for testing"""
    async with async_session() as session:
        # Check if past election already exists
        existing_past = await session.execute(
            select(Election).where(Election.title == "2023 Budget Approval Referendum")
        )
        if existing_past.scalar_one_or_none():
            print("❗ Past election already exists. Skipping.")
            return

        print("Creating additional elections...")

        # Create a past election (ended)
        past_election = Election(
            id=uuid.uuid4(),
            title="2023 Budget Approval Referendum",
            description="Vote on the proposed student activity fee increase.",
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow() - timedelta(days=23),
            is_active=True
        )
        session.add(past_election)
        await session.flush()

        # Candidates for referendum
        referendum_candidates = [
            Candidate(
                id=uuid.uuid4(),
                name="Yes - Approve Fee Increase",
                description="Support the $50 annual increase for enhanced student services.",
                party=None,
                election_id=past_election.id
            ),
            Candidate(
                id=uuid.uuid4(),
                name="No - Reject Fee Increase",
                description="Oppose the fee increase and maintain current funding levels.",
                party=None,
                election_id=past_election.id
            )
        ]

        for candidate in referendum_candidates:
            session.add(candidate)

        # Add some voters to past election
        past_voters = ["alice@example.com", "admin@example.com", "test@example.com"]
        for email in past_voters:
            voter_entry = VoterList(
                id=uuid.uuid4(),
                email=email,
                election_id=past_election.id
            )
            session.add(voter_entry)

        await session.commit()
        print("✅ Additional elections created!")


if __name__ == "__main__":
    async def main():
        print("🚀 Starting election data seeding...")
        try:
            await seed_election_data()
            await create_more_elections()
            print("🎉 All election data seeded successfully!")
        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            raise


    asyncio.run(main())