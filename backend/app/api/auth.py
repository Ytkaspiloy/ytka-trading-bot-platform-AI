from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

def admin_required(fn):
    """Декоратор для проверки прав администратора"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        try:
            user = User.query.get(user_id)
            if not user or not user.is_admin:
                return jsonify({'error': 'Admin access required'}), 403
        except Exception as e:
            logger.error(f"Admin check error: {e}")
            return jsonify({'error': 'Authentication failed'}), 401
        
        return fn(*args, **kwargs)
    return wrapper