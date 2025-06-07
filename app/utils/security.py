import re
import redis
from datetime import datetime, timedelta
from flask import current_app

redis_client = redis.Redis.from_url(current_app.config['REDIS_URL'])


def check_password_strength(password):
    """Check if password meets security requirements"""
    if len(password) < 12:
        return False

    # Must contain uppercase, lowercase, digit, and special character
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False

    return True


def detect_suspicious_activity(user_id, ip_address):
    """Detect suspicious login patterns"""
    current_time = datetime.utcnow()

    # Check for too many failed attempts
    failed_key = f"failed_attempts:{user_id}"
    failed_count = redis_client.get(failed_key)
    if failed_count and int(failed_count) >= 5:
        return True

    # Check for login from multiple IPs in short time
    ip_key = f"login_ips:{user_id}"
    recent_ips = redis_client.smembers(ip_key)
    if len(recent_ips) > 3:
        return True

    # Store current IP with expiration
    redis_client.sadd(ip_key, ip_address)
    redis_client.expire(ip_key, 300)  # 5 minutes

    return False


def rate_limit_check(user_id, action, limit=5, window=60):
    """Generic rate limiting function"""
    key = f"rate_limit:{action}:{user_id}"
    current_count = redis_client.incr(key)

    if current_count == 1:
        redis_client.expire(key, window)

    return current_count <= limit