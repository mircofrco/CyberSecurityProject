from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import redis


def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Set up rate limiting
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        storage_uri=app.config['REDIS_URL']
    )

    # CORS configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": ["https://yourdomain.com"],
            "methods": ["GET", "POST"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.voting.routes import voting_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(voting_bp, url_prefix='/api/voting')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    return app