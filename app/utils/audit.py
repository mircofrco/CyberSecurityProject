from flask import request
from app.models.audit import AuditLog, db
from datetime import datetime


def log_event(event_type, user_id, event_data):
    """Log security-relevant events with tamper detection"""

    # Get the last log entry for hash chaining
    last_log = AuditLog.query.order_by(AuditLog.id.desc()).first()
    previous_hash = last_log.event_hash if last_log else None

    # Create new audit log entry
    audit_log = AuditLog(
        event_type=event_type,
        user_id=user_id,
        event_data=event_data,
        ip_address=request.remote_addr if request else None,
        user_agent=request.headers.get('User-Agent') if request else None
    )

    # Generate hash for tamper detection
    audit_log.generate_hash(previous_hash)

    db.session.add(audit_log)
    db.session.commit()

    return audit_log