from flask import Blueprint, request, jsonify
from app.models import db,User
from flask_jwt_extended import create_access_token,jwt_required
auth_b_p = Blueprint('auth',__name__)


@auth_b_p.route('/register',methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({"error":"Missing required fields"}), 400
    
    role =data.get("role","staff")
    if role not in ["staff","manager","admin"]:
        return jsonify({"error":"Invalid role"}),400

    if User.query.filter_by(username = data['username']).first():
        return jsonify({"error":"Username already existis"}),400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400

    new_user = User(
        username=data['username'],
        email=data["email"],
        role=role
    )
    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@auth_b_p.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing username or password"}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({"message": "Login successful", "access_token": access_token}), 200




@auth_b_p.route("/users",methods=['GET'])
@jwt_required()
def get_all_users():
    users = User.query.all()
    return jsonify([{"id":user.id,"username":user.username,"email":user.email}for user in users]), 200


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

    if "username" in data:
        user.username = data["username"]
    if "email" in data:
        user.email = data["email"]
    if "password" in data:
        user.set_password(data["password"])
    if "role" in data:
        user.role = data["role"]

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
