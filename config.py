import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-secure-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://username:password@localhost/secure_voting'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')  # Fernet key
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'