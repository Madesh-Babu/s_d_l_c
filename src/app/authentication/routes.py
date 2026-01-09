from flask import Blueprint, request, jsonify
from Inventory_Management_API.src.models.models import db,User
from flask_jwt_extended import create_access_token,jwt_required,get_jwt_identity
from Inventory_Management_API.src.models.schemas import UserCreate, UserLogin, UserUpdate
from pydantic import ValidationError
from app.core.logging import get_logger, log_user_action, log_api_error

auth_b_p = Blueprint('auth',__name__)
logger = get_logger(__name__)


@auth_b_p.route('/register',methods=['POST'])
def register():
    data = request.get_json()

    logger.info("User registration attempt", 
                username=data.get('username'), 
                email=data.get('email'),
                role=data.get('role'))

    try:
        user_data = UserCreate(**data)
        
        # Check for existing username and email
        if User.query.filter_by(username=user_data.username).first():
            logger.warning("Registration failed - username already exists", 
                          username=user_data.username)
            return jsonify({"error":"Username already exists"}),400
        
        if User.query.filter_by(email=user_data.email).first():
            logger.warning("Registration failed - email already registered", 
                          email=user_data.email)
            return jsonify({"error":"Email already registered"}),400

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
                    role=new_user.role)
        
        log_user_action("user_registered", str(new_user.id), 
                        username=new_user.username, 
                        role=new_user.role)

        return jsonify({"message": "User registered successfully"}), 201
    
    except ValidationError as e:
        logger.error("Registration validation error", 
                     error=str(e), 
                     username=data.get('username'))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error("Registration failed with unexpected error", 
                     error=str(e), 
                     exc_info=True)
        return jsonify({"error": "Registration failed"}), 500


@auth_b_p.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    logger.info("User login attempt", username=data.get('username'))

    try:
        login_data = UserLogin(**data)
        
        user = User.query.filter_by(username=login_data.username).first()

        if not user or not user.check_password(login_data.password):
            logger.warning("Login failed - invalid credentials", 
                          username=login_data.username)
            log_api_error("invalid_credentials", "AUTH001", 
                          username=login_data.username)
            return jsonify({"error": "Invalid username or password"}), 401

        access_token = create_access_token(identity=str(user.id))

        logger.info("User login successful", 
                    user_id=user.id, 
                    username=user.username, 
                    role=user.role)
        
        log_user_action("user_login", str(user.id), 
                        username=user.username, 
                        role=user.role)

        return jsonify({"message": "Login successful", "access_token": access_token}), 200
    
    except ValidationError as e:
        logger.error("Login validation error", 
                     error=str(e), 
                     username=data.get('username'))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error("Login failed with unexpected error", 
                     error=str(e), 
                     username=data.get('username'),
                     exc_info=True)
        return jsonify({"error": "Login failed"}), 500




@auth_b_p.route("/users",methods=['GET'])
@jwt_required()
def get_all_users():
    current_user_id = get_jwt_identity()
    logger.info("Get all users request", user_id=current_user_id)
    
    try:
        users = User.query.all()
        user_list = [{"id":user.id,"username":user.username,"email":user.email} 
                     for user in users]
        
        logger.info("Users retrieved successfully", 
                    user_id=current_user_id, 
                    user_count=len(user_list))
        
        return jsonify(user_list), 200
    except Exception as e:
        logger.error("Failed to retrieve users", 
                     user_id=current_user_id, 
                     error=str(e), 
                     exc_info=True)
        return jsonify({"error": "Failed to retrieve users"}), 500


@auth_b_p.route('/<int:user_id>',methods=['GET'])
@jwt_required()
def get_user(user_id):
    user=User.query.get_or_404(user_id)
    return jsonify({"id":user.id,"username":user.username,"email":user.email}),200


@auth_b_p.route("/update", methods=["PUT"])
@jwt_required()
def update_user():
    data = request.get_json()
    user_id = data.get("id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

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


@auth_b_p.route("/delete", methods=["DELETE"])
@jwt_required()
def delete_user():
    data = request.get_json()
    user_id = data.get("id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User {user.username} deleted successfully"}), 200
