from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.service import CategoryService,validate_category_data
from app.utils.roles_required import role_required
from app.interfaces import ICategoryCreator,ICategoryDeleter,ICategoryReader,ICategoryUpdater
from app import db

categories_b_p = Blueprint("categories", __name__)

category_service: ICategoryUpdater | ICategoryCreator | ICategoryReader | ICategoryDeleter = CategoryService() 

@categories_b_p.route("/", methods=["POST"])
@jwt_required()
@role_required("admin","manager")
def create_category():
    data = request.get_json()
    valid ,error = validate_category_data(data)
    
    if not valid:
        return jsonify({"error":error}),400
    
    if not data or "name" not in data:
        return jsonify({"error": "Category name is required"}), 400

    category, err = category_service.create_category(data["name"])
    if err:
        return jsonify(err), 400

    return jsonify({
        "message": "Category created successfully",
        "category": {"id": category.id, "name": category.name}
    }), 201


@categories_b_p.route("/", methods=["GET"])
@jwt_required()
def get_categories():
    categories = category_service.get_all_categories()
    return jsonify([{"id": c.id, "name": c.name} for c in categories]), 200


@categories_b_p.route("/<int:category_id>", methods=["GET"])
@jwt_required()
def get_category(category_id):
    category = category_service.get_category(category_id)
    return jsonify({"id": category.id, "name": category.name}), 200


@categories_b_p.route("/update", methods=["PUT"])
@jwt_required()
@role_required("admin", "manager")
def update_category():
    data = request.get_json()

    # Validate request body
    if not data or "id" not in data:
        return jsonify({"error": "Category ID is required"}), 400

    category_id = data["id"]

    # Delegate the actual update logic to the service layer
    updated_category = category_service.update_category(category_id, data)
    if not updated_category:
        return jsonify({"error": "Category not found"}), 404

    return jsonify({
        "message": "Category updated successfully",
        "category": updated_category.to_dict()
    }), 200



@categories_b_p.route("/<int:category_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_category(category_id):
    category_service.delete_category(category_id)
    return jsonify({"message": "Category deleted successfully"}), 200
