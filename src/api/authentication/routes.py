from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.models import db,User
from flask_jwt_extended import create_access_token,jwt_required,get_jwt_identity
from src.models.schemas import UserCreate, UserLogin, UserUpdate
from pydantic import ValidationError
from src.core.logging import get_logger, log_user_action, log_api_error
from src.core.validation import UserValidator, EmailValidator, PasswordValidator
from src.core.config import settings
from src.core.exceptions import (
    ValidationErrorException, AuthenticationError, NotFoundError, 
    ConflictError, DatabaseError, exception_handler
)

auth_b_p = Blueprint('auth',__name__)
logger = get_logger(__name__)


@auth_b_p.route('/register',methods=['POST'])
def register():
    """Register a new user with comprehensive exception handling."""
    try:
        # print(request.get_json(),'rrr')
        data = request.get_json()
        
        if not data:
            raise ValidationErrorException("No data provided", details={"required_fields": ["username", "email", "password", "role"]})

        logger.info("User registration attempt", 
                    username=data.get('username'), 
                    email=data.get('email'),
                    role=data.get('role'))

        # Validate input data with Pydantic schemas
        user_data = UserCreate(**data)
        # print(user_data,'uuu')
        
        # Enhanced validation using new Pydantic validators
        try:
            # Validate email
            EmailValidator(email=user_data.email)
            
            # Validate password with regex strictness
            password_validator = PasswordValidator(password=user_data.password)
            password_strength = PasswordValidator.get_password_strength(user_data.password)
            
            # Combined user validation
            UserValidator(
                email=user_data.email,
                password=user_data.password,
                username=user_data.username
            )
            
            logger.info("Validation passed", 
                       email=user_data.email,
                       username=user_data.username,
                       password_strength=password_strength['strength'])
            
        except ValidationError as e:
            raise ValidationErrorException(str(e), details={"validation_type": "email_password"})
        
        except Exception as e:
            raise ValidationErrorException(str(e))
        
        # Check for existing username and email
        if User.query.filter_by(username=user_data.username).first():
            raise ConflictError("Username already exists", details={"field": "username", "value": user_data.username})
        
        if User.query.filter_by(email=user_data.email).first():
            raise ConflictError("Email already registered", details={"field": "email", "value": user_data.email})

        # Create new user
        try:
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                role=user_data.role
            )
            new_user.set_password(user_data.password)

            db.session.add(new_user)
            db.session.commit()

            logger.info("User registered successfully", 
                        user_id=new_user.id, 
                        username=new_user.username, 
                        role=new_user.role,
                        password_strength=password_strength)
            
            log_user_action("user_registered", str(new_user.id), 
                            username=new_user.username, 
                            role=new_user.role)

            return jsonify({
                "message": "User registered successfully",
                "user_id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "role": new_user.role,
                "password_strength": password_strength
            }), 201
            
        except Exception as e:
            db.session.rollback()
            raise DatabaseError("Failed to create user", details={"username": user_data.username, "email": user_data.email})
    
    except ValidationErrorException as e:
        logger.warning("Registration validation error", error=str(e), username=data.get('username') if 'data' in locals() else None)
        return exception_handler.handle_exception(e)
    
    except ConflictError as e:
        logger.warning("Registration conflict error", error=str(e), username=data.get('username') if 'data' in locals() else None)
        return exception_handler.handle_exception(e)
    
    except DatabaseError as e:
        logger.error("Registration database error", error=str(e), username=data.get('username') if 'data' in locals() else None)
        return exception_handler.handle_exception(e)
    
    except Exception as e:
        logger.error("Registration failed with unexpected error", error=str(e), exc_info=True)
        return exception_handler.handle_exception(e)


@auth_b_p.route('/login', methods=['POST'])
def login():
    """Authenticate user with comprehensive exception handling."""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationErrorException("No data provided", details={"required_fields": ["username", "password"]})

        logger.info("User login attempt", username=data.get('username'))
        
        login_data = UserLogin(**data)
        
        # Find user
        user = User.query.filter_by(username=login_data.username).first()
        
        if not user:
            raise AuthenticationError("Invalid username or password", details={"username": login_data.username})
        
        # Check password
        if not user.check_password(login_data.password):
            raise AuthenticationError("Invalid username or password", details={"username": login_data.username})
        
        # Generate JWT token
        try:
            access_token = create_access_token(identity=str(user.id))
        except Exception as e:
            raise DatabaseError("Failed to generate access token", details={"user_id": user.id})

        logger.info("User login successful", 
                    user_id=user.id, 
                    username=user.username, 
                    role=user.role)
        
        log_user_action("user_login", str(user.id), 
                        username=user.username, 
                        role=user.role)

        return jsonify({
            "message": "Login successful", 
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }), 200
    
    except ValidationErrorException as e:
        logger.warning("Login validation error", error=str(e), username=data.get('username') if 'data' in locals() else None)
        return exception_handler.handle_exception(e)
    
    except AuthenticationError as e:
        logger.warning("Login authentication error", error=str(e), username=data.get('username') if 'data' in locals() else None)
        return exception_handler.handle_exception(e)
    
    except DatabaseError as e:
        logger.error("Login database error", error=str(e), username=data.get('username') if 'data' in locals() else None)
        return exception_handler.handle_exception(e)
    
    except Exception as e:
        logger.error("Login failed with unexpected error", error=str(e), username=data.get('username') if 'data' in locals() else None, exc_info=True)
        return exception_handler.handle_exception(e)




@auth_b_p.route("/users",methods=['GET'])
def get_all_users():
    # Simple bypass for development
    if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
        logger.info("Get all users request (BYPASSED)")
        users = User.query.all()
        user_list = [{"id":user.id,"username":user.username,"email":user.email} 
                     for user in users]
        return jsonify({
            "users": user_list,
            "auth_bypassed": True,
            "message": "Authentication bypassed in development"
        }), 200
    
    # Normal JWT verification for production
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        logger.info("Get all users request", user_id=current_user_id)
        
        users = User.query.all()
        user_list = [{"id":user.id,"username":user.username,"email":user.email} 
                     for user in users]
        
        logger.info("Users retrieved successfully", 
                    user_id=current_user_id, 
                    user_count=len(user_list))
        
        return jsonify(user_list), 200
    except Exception as e:
        logger.error("JWT verification failed", error=str(e))
        return jsonify({
            "error": "Authentication required",
            "message": "Valid JWT token required"
        }), 401


@auth_b_p.route('/<int:user_id>',methods=['GET'])
def get_user(user_id):
    # Simple bypass for development
    if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
        logger.info(f"Get user {user_id} request (BYPASSED)")
        user = User.query.get_or_404(user_id)
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "auth_bypassed": True,
            "message": "Authentication bypassed in development"
        }), 200
    
    # Normal JWT verification for production
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request()
        user = User.query.get_or_404(user_id)
        return jsonify({"id":user.id,"username":user.username,"email":user.email}),200
    except Exception as e:
        logger.error("JWT verification failed", error=str(e))
        return jsonify({
            "error": "Authentication required",
            "message": "Valid JWT token required"
        }), 401


@auth_b_p.route('/<int:user_id>',methods=['PUT'])
def update_user(user_id):
    # Simple bypass for development
    if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
        logger.info(f"Update user {user_id} request (BYPASSED)")
        data = request.get_json()
        user = User.query.get_or_404(user_id)
        
        try:
            update_data = UserUpdate(**data)
            
            # Update only provided fields
            if update_data.username is not None:
                user.username = update_data.username
            if update_data.email is not None:
                user.email = update_data.email
            if update_data.password is not None:
                user.set_password(update_data.password)
            if update_data.role is not None:
                user.role = update_data.role

            db.session.commit()
            return jsonify({
                "message": "User updated successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role
                },
                "auth_bypassed": True
            }), 200
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400
    
    # Normal JWT verification for production
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request()
        data = request.get_json()
        user = User.query.get_or_404(user_id)

        try:
            update_data = UserUpdate(**data)
            
            # Update only provided fields
            if update_data.username is not None:
                user.username = update_data.username
            if update_data.email is not None:
                user.email = update_data.email
            if update_data.password is not None:
                user.set_password(update_data.password)
            if update_data.role is not None:
                user.role = update_data.role

            db.session.commit()
            return jsonify({
                "message": "User updated",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role
                }
            }), 200
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error("JWT verification failed", error=str(e))
        return jsonify({
            "error": "Authentication required",
            "message": "Valid JWT token required"
        }), 401


@auth_b_p.route('/<int:user_id>',methods=['DELETE'])
def delete_user(user_id):
    # Simple bypass for development
    if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
        logger.info(f"Delete user {user_id} request (BYPASSED)")
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({
            "message": f"User {user.username} deleted successfully",
            "auth_bypassed": True
        }), 200
    
    # Normal JWT verification for production
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request()
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"User {user.username} deleted successfully"}),200
    except Exception as e:
        logger.error("JWT verification failed", error=str(e))
        return jsonify({
            "error": "Authentication required",
            "message": "Valid JWT token required"
        }), 401


# Development-only bypass endpoint
@auth_b_p.route('/dev-login', methods=['POST'])
def dev_login():
    """Development login endpoint that bypasses authentication."""
    if not settings.is_development():
        return jsonify({
            "error": "Endpoint not available",
            "message": "This endpoint is only available in development mode"
        }), 404
    
    if not settings.feature_toggles.BYPASS_AUTH:
        return jsonify({
            "error": "Bypass disabled",
            "message": "Authentication bypass is not enabled"
        }), 403
    
    # Create mock development user token
    dev_user = {
        'id': '1',
        'username': 'dev_user',
        'email': 'dev@example.com',
        'role': 'admin'
    }
    
    # Create a mock token (in real implementation, use JWT)
    mock_token = f"dev_token_{datetime.now().timestamp()}"
    
    logger.info("Development login completed", user=dev_user)
    
    return jsonify({
        "message": "Development login successful",
        "access_token": mock_token,
        "token_type": "bearer",
        "user": dev_user,
        "bypass_enabled": True,
        "environment": settings.ENVIRONMENT
    }), 200


@auth_b_p.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """Change user password with validation."""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    logger.info("Password change attempt", user_id=current_user_id)
    
    try:
        current_password = data.get("current_password")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        
        # Validate input
        if not all([current_password, new_password, confirm_password]):
            return jsonify({"error": "All password fields are required"}), 400
        
        # Get user
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Verify current password
        if not user.check_password(current_password):
            logger.warning("Password change failed - incorrect current password", 
                          user_id=current_user_id)
            return jsonify({"error": "Current password is incorrect"}), 400
        
        # Validate new password with regex strictness
        try:
            password_validator = PasswordValidator(password=new_password)
            password_strength = PasswordValidator.get_password_strength(new_password)
            
            logger.info("New password validation passed", 
                       user_id=current_user_id,
                       password_strength=password_strength['strength'])
            
        except ValidationError as e:
            logger.warning("Password change failed - validation errors", 
                          user_id=current_user_id,
                          errors=str(e))
            
            return jsonify({
                "error": "Password validation failed",
                "details": str(e),
                "password_strength": password_strength if 'password_strength' in locals() else None
            }), 400
        
        except Exception as e:
            logger.warning("Password change failed - validation error", 
                          user_id=current_user_id,
                          error=str(e))
            
            return jsonify({
                "error": "Password validation failed",
                "details": str(e)
            }), 400
        
        # Change password
        user.set_password(new_password)
        db.session.commit()
        
        logger.info("Password changed successfully", 
                    user_id=current_user_id,
                    password_strength=password_strength)
        
        log_user_action("password_changed", str(current_user_id))
        
        return jsonify({
            "message": "Password changed successfully",
            "password_strength": password_strength
        }), 200
        
    except Exception as e:
        logger.error("Password change failed with unexpected error", 
                     user_id=current_user_id,
                     error=str(e), 
                     exc_info=True)
        return jsonify({"error": "Password change failed"}), 500


@auth_b_p.route("/validate-password", methods=["POST"])
def validate_password():
    """Validate password strength without changing it."""
    data = request.get_json()
    password = data.get("password")
    username = data.get("username")
    email = data.get("email")
    
    if not password:
        return jsonify({"error": "Password is required"}), 400
    
    validator = UserValidator()
    validation_result = validator.validate_user_registration(
        email or "test@example.com", 
        password, 
        username
    )
    
    return jsonify({
        "is_valid": validation_result["password"]["is_valid"],
        "strength": validation_result["password_strength"],
        "details": validation_result["password"]
    })
