from app.models import db
from datetime import datetime
import hashlib
import json


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)  # LOGIN, VOTE, ADMIN_ACTION, etc.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_data = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    hash_chain = db.Column(db.String(64))  # Hash of previous log entry
    event_hash = db.Column(db.String(64), nullable=False)  # Hash of this entry

    def generate_hash(self, previous_hash=None):
        """Generate cryptographic hash for tamper detection"""
        data = {
            'event_type': self.event_type,
            'user_id': self.user_id,
            'event_data': self.event_data,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'previous_hash': previous_hash or ''
        }
        hash_input = json.dumps(data, sort_keys=True).encode()
        self.event_hash = hashlib.sha256(hash_input).hexdigest()
        self.hash_chain = previous_hash
        return self.event_hash