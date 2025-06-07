from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from datetime import datetime

from app.models.user import User
from app.models.vote import Vote, Election, db
from app.voting.crypto import VoteEncryption
from app.utils.audit import log_event
from app.utils.security import rate_limit_check

voting_bp = Blueprint('voting', __name__)


@voting_bp.route('/elections', methods=['GET'])
@jwt_required()
def get_active_elections():
    """Get list of active elections"""
    current_time = datetime.utcnow()
    elections = Election.query.filter(
        Election.is_active == True,
        Election.start_time <= current_time,
        Election.end_time > current_time
    ).all()

    return jsonify({
        'elections': [{
            'id': e.id,
            'title': e.title,
            'description': e.description,
            'candidates': e.candidates,
            'end_time': e.end_time.isoformat()
        } for e in elections]
    }), 200


@voting_bp.route('/vote', methods=['POST'])
@jwt_required()
def cast_vote():
    """Cast an encrypted vote"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Check rate limiting
    if not rate_limit_check(user_id, 'vote_attempt', limit=3, window=300):
        return jsonify({'error': 'Too many vote attempts'}), 429

    data = request.get_json()
    if not all(k in data for k in ['election_id', 'candidate_id']):
        return jsonify({'error': 'Missing required fields'}), 400

    election = Election.query.get(data['election_id'])
    if not election or not election.is_active:
        return jsonify({'error': 'Election not found or inactive'}), 404

    # Check if election is currently running
    current_time = datetime.utcnow()
    if not (election.start_time <= current_time <= election.end_time):
        return jsonify({'error': 'Election is not currently running'}), 400

    # Check if user already voted in this election
    user_vote_hash = VoteEncryption.generate_vote_hash(user_id, election.id)
    existing_vote = Vote.query.filter_by(
        vote_hash=user_vote_hash[:32],  # Use first 32 chars for lookup
        election_id=election.id
    ).first()

    if existing_vote:
        return jsonify({'error': 'User has already voted in this election'}), 409

    # Validate candidate
    if data['candidate_id'] not in [c['id'] for c in election.candidates]:
        return jsonify({'error': 'Invalid candidate'}), 400

    # Prepare vote data
    vote_data = {
        'candidate_id': data['candidate_id'],
        'timestamp': current_time.isoformat(),
        'election_id': election.id
    }

    # Encrypt vote
    encrypted_vote = VoteEncryption.encrypt_vote(vote_data, election.public_key)

    # Generate anonymous vote hash
    vote_hash = VoteEncryption.generate_vote_hash(user_id, election.id)

    # Store vote
    vote = Vote(
        vote_hash=vote_hash[:32],
        encrypted_vote=encrypted_vote,
        election_id=election.id
    )

    # Mark user as voted
    user.has_voted = True

    db.session.add(vote)
    db.session.commit()

    # Log vote cast (without revealing vote content)
    log_event('VOTE_CAST', user_id, {
        'election_id': election.id,
        'vote_hash': vote_hash[:16],  # Partial hash for audit
        'ip_address': request.remote_addr
    })

    return jsonify({
        'message': 'Vote cast successfully',
        'vote_receipt': vote_hash[:16]  # Partial hash for voter verification
    }), 201


@voting_bp.route('/elections/<int:election_id>/results', methods=['GET'])
def get_election_results(election_id):
    """Get public election results"""
    election = Election.query.get(election_id)
    if not election:
        return jsonify({'error': 'Election not found'}), 404

    # Only show results after election ends
    if datetime.utcnow() < election.end_time:
        return jsonify({'error': 'Election still in progress'}), 400

    # Decrypt and tally votes (this would be done by authorized personnel)
    votes = Vote.query.filter_by(election_id=election_id).all()

    # For demonstration, return vote count without decrypting
    # In practice, this would require the private key and proper authorization
    results = {
        'election': {
            'id': election.id,
            'title': election.title,
            'total_votes': len(votes),
            'candidates': election.candidates
        },
        'note': 'Vote tallying requires authorized decryption process'
    }

    return jsonify(results), 200