from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from flask import jsonify
from werkzeug.exceptions import Forbidden, Unauthorized
from app.models import User

def role_required(*roles):
    """Restrict route access to specific roles (checks DB or token claims)."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            claims = get_jwt()

            token_role = claims.get("role")
            if token_role:
                if token_role not in roles:
                    raise Forbidden("Access forbidden: insufficient permissions")
                return fn(*args, **kwargs)

            try:
                user = User.query.get(int(identity))
                if not user:
                    raise Unauthorized("User not found")
                if user.role not in roles:
                    raise Forbidden("Access forbidden: insufficient permissions")
                return fn(*args, **kwargs)
            except ValueError:
                raise Unauthorized("Invalid token identity type")
        return decorator
    return wrapper
