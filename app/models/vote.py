from app.models import db
from datetime import datetime
import json


class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    vote_hash = db.Column(db.String(64), unique=True, nullable=False)  # Anonymous identifier
    encrypted_vote = db.Column(db.Text, nullable=False)  # Encrypted vote content
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)


class Election(db.Model):
    __tablename__ = 'elections'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    candidates = db.Column(db.JSON, nullable=False)  # List of candidates
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    public_key = db.Column(db.Text, nullable=False)  # For vote encryption
    private_key_encrypted = db.Column(db.Text, nullable=False)  # Encrypted private key
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    votes = db.relationship('Vote', backref='election', lazy=True)