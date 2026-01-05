from flask import Blueprint, jsonify, request
from services.category_service.models import Category
from services.category_service.extensions import db

category_blueprint = Blueprint("category", __name__)

# GET all categories
@category_blueprint.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()

    return jsonify([
        {
            "id": c.id,
            "user_id": c.user_id,
            "name": c.name,
            "budget_amount": float(c.budget_amount) if c.budget_amount else None
        }
        for c in categories
    ]), 200
@category_blueprint.route("/category", methods=["GET"])
def get_categories():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    categories = Category.query.filter_by(user_id=user_id).all()

    return jsonify([c.to_dict() for c in categories]), 200


# GET single category
@category_blueprint.route("/category/<int:category_id>", methods=["GET"])
def get_category(category_id):
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id
    ).first_or_404()

    return jsonify(category.to_dict()), 200

# UPDATE category (name + budget_amount)
@category_blueprint.route("/category/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    data = request.get_json()

    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id
    ).first_or_404()

    # Update name
    if "name" in data:
        category.name = data["name"]

    # Update budget amount
    if "budget_amount" in data:
        category.budget_amount = data["budget_amount"]

    db.session.commit()
    return jsonify(category.to_dict()), 200


# DELETE category
@category_blueprint.route("/category/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    data = request.get_json() or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id
    ).first_or_404()

    db.session.delete(category)
    db.session.commit()

    return jsonify({"message": "Category deleted"}), 200

