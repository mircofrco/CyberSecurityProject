from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity
from functools import wraps

from app.models.user import User
from app.models.vote import Election, Vote, db
from app.models.audit import AuditLog
from app.voting.crypto import VoteEncryption
from app.utils.audit import log_event

admin_bp = Blueprint('admin', __name__)


def require_role(required_role):
    """Decorator to require specific role"""

    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            claims = get_jwt_claims()
            if claims.get('role') != required_role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@admin_bp.route('/elections', methods=['POST'])
@require_role('admin')
def create_election():
    """Create a new election"""
    user_id = get_jwt_identity()
    data = request.get_json()

    required_fields = ['title', 'description', 'candidates', 'start_time', 'end_time']
    if not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Generate encryption keypair for this election
    private_key, public_key = VoteEncryption.generate_election_keypair()

    # TODO: Encrypt private key with admin key or store securely
    election = Election(
        title=data['title'],
        description=data['description'],
        candidates=data['candidates'],
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']),
        public_key=public_key,
        private_key_encrypted=private_key  # Should be encrypted in production
    )

    db.session.add(election)
    db.session.commit()

    log_event('ELECTION_CREATED', user_id, {
        'election_id': election.id,
        'title': election.title,
        'ip_address': request.remote_addr
    })

    return jsonify({
        'message': 'Election created successfully',
        'election_id': election.id
    }), 201


@admin_bp.route('/elections/<int:election_id>/activate', methods=['POST'])
@require_role('admin')
def activate_election(election_id):
    """Activate an election"""
    user_id = get_jwt_identity()
    election = Election.query.get(election_id)

    if not election:
        return jsonify({'error': 'Election not found'}), 404

    election.is_active = True
    db.session.commit()

    log_event('ELECTION_ACTIVATED', user_id, {
        'election_id': election.id,
        'ip_address': request.remote_addr
    })

    return jsonify({'message': 'Election activated'}), 200


@admin_bp.route('/audit/logs', methods=['GET'])
@require_role('admin')
def get_audit_logs():
    """Get audit logs with integrity verification"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Verify log chain integrity
    integrity_check = verify_audit_chain()

    log_event('AUDIT_ACCESS', user_id, {
        'page': page,
        'per_page': per_page,
        'ip_address': request.remote_addr
    })

    return jsonify({
        'logs': [{
            'id': log.id,
            'event_type': log.event_type,
            'timestamp': log.timestamp.isoformat(),
            'event_data': log.event_data,
            'ip_address': log.ip_address
        } for log in logs.items],
        'pagination': {
            'page': logs.page,
            'pages': logs.pages,
            'per_page': logs.per_page,
            'total': logs.total
        },
        'integrity_check': integrity_check
    }), 200


def verify_audit_chain():
    """Verify the integrity of the audit log chain"""
    logs = AuditLog.query.order_by(AuditLog.id).all()

    for i, log in enumerate(logs):
        if i == 0:
            continue

        previous_log = logs[i - 1]
        if log.hash_chain != previous_log.event_hash:
            return {
                'status': 'COMPROMISED',
                'broken_at': log.id,
                'message': 'Audit log chain integrity violation detected'
            }

    return {
        'status': 'INTACT',
        'message': 'Audit log chain integrity verified',
        'total_logs': len(logs)
    }