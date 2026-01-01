from flask import Blueprint, jsonify, request
from models import Category
from extensions import db
from decimal import Decimal

category_blueprint = Blueprint("category", __name__)

# GET all categories
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

    if "budget_amount" in data:
        category.budget_amount = (
            Decimal(str(data["budget_amount"]))
            if data["budget_amount"] is not None
            else None
        )


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

