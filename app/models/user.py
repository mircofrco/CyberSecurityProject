from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import pyotp
import secrets

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email_encrypted = db.Column(db.Text, nullable=False)  # Encrypted email
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='voter')  # voter, admin, auditor
    is_verified = db.Column(db.Boolean, default=False)
    has_voted = db.Column(db.Boolean, default=False)
    totp_secret = db.Column(db.String(32))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_email(self, email, encryption_key):
        f = Fernet(encryption_key)
        self.email_encrypted = f.encrypt(email.encode()).decode()

    def get_email(self, encryption_key):
        f = Fernet(encryption_key)
        return f.decrypt(self.email_encrypted.encode()).decode()

    def generate_totp_secret(self):
        self.totp_secret = pyotp.random_base32()
        return self.totp_secret

    def verify_totp(self, token):
        if not self.totp_secret:
            return False
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token, valid_window=1)