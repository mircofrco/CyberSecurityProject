from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pyotp
import qrcode
import io
import base64

from app.models.user import User, db
from app.utils.audit import log_event
from app.utils.security import check_password_strength, detect_suspicious_activity

auth_bp = Blueprint('auth', __name__)
limiter = Limiter(key_func=get_remote_address)


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()

    # Validate input
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check password strength
    if not check_password_strength(data['password']):
        return jsonify({'error': 'Password does not meet security requirements'}), 400

    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409

    # Create new user
    user = User(username=data['username'], role='voter')
    user.set_password(data['password'])
    user.set_email(data['email'], current_app.config['ENCRYPTION_KEY'])

    # Generate TOTP secret
    totp_secret = user.generate_totp_secret()

    db.session.add(user)
    db.session.commit()

    # Generate QR code for TOTP setup
    totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
        user.username,
        issuer_name="Secure Voting System"
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_code = base64.b64encode(buffer.getvalue()).decode()

    # Log registration
    log_event('USER_REGISTRATION', user.id, {
        'username': user.username,
        'ip_address': request.remote_addr
    })

    return jsonify({
        'message': 'User registered successfully',
        'qr_code': qr_code,
        'manual_entry_key': totp_secret
    }), 201


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()

    if not all(k in data for k in ['username', 'password', 'totp_code']):
        return jsonify({'error': 'Missing required fields'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        # Log failed login attempt
        log_event('FAILED_LOGIN', None, {
            'username': data['username'],
            'ip_address': request.remote_addr,
            'reason': 'invalid_credentials'
        })
        return jsonify({'error': 'Invalid credentials'}), 401

    # Verify TOTP
    if not user.verify_totp(data['totp_code']):
        log_event('FAILED_LOGIN', user.id, {
            'username': user.username,
            'ip_address': request.remote_addr,
            'reason': 'invalid_totp'
        })
        return jsonify({'error': 'Invalid TOTP code'}), 401

    # Check for suspicious activity
    if detect_suspicious_activity(user.id, request.remote_addr):
        log_event('SUSPICIOUS_LOGIN', user.id, {
            'username': user.username,
            'ip_address': request.remote_addr
        })
        return jsonify({'error': 'Account temporarily locked due to suspicious activity'}), 423

    # Generate JWT token
    access_token = create_access_token(
        identity=user.id,
        additional_claims={'role': user.role, 'username': user.username}
    )

    # Log successful login
    log_event('SUCCESSFUL_LOGIN', user.id, {
        'username': user.username,
        'ip_address': request.remote_addr
    })

    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'has_voted': user.has_voted
        }
    }), 200