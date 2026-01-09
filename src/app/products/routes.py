from flask import Blueprint,request,jsonify
from Inventory_Management_API.src.models.models import db, Product,Category
from flask_jwt_extended import jwt_required
from Inventory_Management_API.src.services.service import ProductService,DiscountedProductService,validate_product_data
from app.utils.roles_required import role_required
from Inventory_Management_API.src.app.core.interfaces import IProductCreator,IProductReader,IProductUpdater,IProductDeleter
from Inventory_Management_API.src.models.schemas import ProductCreate, ProductUpdate, DiscountRequest
from pydantic import ValidationError

products_b_p = Blueprint("products", __name__)

product_service: IProductCreator | IProductReader | IProductUpdater | IProductDeleter = ProductService()

@products_b_p.route("/", methods=["POST"])
@jwt_required()
@role_required("admin","manager")
def add_product():
    data = request.get_json()
    
    try:
        product_data = ProductCreate(**data)
        valid, error = validate_product_data(data)
        if not valid:
            return jsonify({"error": error}), 400
        
        product = product_service.create_product(data)
        return jsonify({"message": "Product added", "product": product.to_dict()}), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400


@products_b_p.route("/", methods=["GET"])
@jwt_required()
def get_all_products():
    products = product_service.get_all_products()
    return jsonify([p.to_dict() for p in products])


@products_b_p.route("/<int:product_id>", methods=["GET"])
@jwt_required()
def get_products(product_id):
    product = product_service.get_products(product_id)
    if not product:
        return jsonify({'error':"Product not found"}),404
    return jsonify(product.to_dict())


@products_b_p.route("/update", methods=["PUT"])
@jwt_required()
@role_required("admin","manager")
def update_product():
    
    data = request.get_json()
    if "id" not in data:
        return jsonify({"error": "Product ID is required"}), 400

    try:
        update_data = ProductUpdate(**data)
        updated_product = product_service.update_product(data["id"], data)
        if not updated_product:
            return jsonify({"error": "Product not found"}), 404

        return jsonify({"message": "Product updated", "product": updated_product.to_dict()}),200
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400



@products_b_p.route("/delete", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_product():
    data = request.get_json()
    if "id" not in data:
        return jsonify({"error": "Product ID is required"}), 400

    success = product_service.delete_product(data["id"])
    if not success:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"message": "Product deleted"}),200


@products_b_p.route("/discount", methods=["PATCH"])
@jwt_required()
@role_required("admin","manager")
def discount_product():
    data = request.get_json()

    try:
        discount_request = DiscountRequest(**data)
        
        product = Product.query.get(discount_request.id)

        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        updated = DiscountedProductService.apply_discount(product, discount_request.discount, discount_request.tax)
        return jsonify({
            "message": f"Applied {discount_request.discount}% discount and {discount_request.tax}% tax",
            "new_price": updated.price
        }), 200
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400