import os
from flask import Flask, request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from models import Category
from extensions import db

category_api = Blueprint("category_api", __name__)

# Default categories
DEFAULT_CATEGORIES = [
    "Food",
    "Transport",
    "Housing",
    "Utilities",
    "Entertainment",
    "Healthcare",
    "Education",
    "Savings",
    "Other"
]

# Health check
@category_api.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Category service is running"}), 200

# Get all categories (with default seeding)
@category_api.route("/category", methods=["GET"])
def get_categories():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    categories = Category.query.filter_by(user_id=user_id).all()

    if not categories:
        for name in DEFAULT_CATEGORIES:
            db.session.add(Category(name=name, user_id=user_id))
        db.session.commit()
        categories = Category.query.filter_by(user_id=user_id).all()

    return jsonify([
        {"id": c.id, "name": c.name, "budget_amount": float(c.budget_amount) if c.budget_amount else None, "user_id": c.user_id}
        for c in categories
    ]), 200

# Get single category
@category_api.route("/category/<int:category_id>", methods=["GET"])
def get_category(category_id):
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id
    ).first()

    if not category:
        return jsonify({"error": "Category not found"}), 404

    return jsonify({
        "id": category.id,
        "name": category.name,
        "user_id": category.user_id
    }), 200

# Create category
@category_api.route("/category", methods=["POST"])
def create_category():
    data = request.json
    name = data.get("name")
    budget_amount = data.get("budget_amount")
    user_id = data.get("user_id")
    print(data)
    if not name or not user_id:
        return jsonify({"error": "name and user_id are required"}), 400

    # Check if category name already exists for this user
    existing = Category.query.filter_by(name=name, user_id=user_id).first()
    if existing:
        return jsonify({"error": "Category name already exists for this user"}), 409

    category = Category(name=name, budget_amount=budget_amount, user_id=user_id)
    db.session.add(category)
    db.session.commit()

    return jsonify({
        "id": category.id,
        "name": category.name,
        "budget_amount": float(category.budget_amount) if category.budget_amount else None,
        "user_id": category.user_id
    }), 201

# Update category
@category_api.route("/category/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    data = request.json
    name = data.get("name")
    budget_amount = data.get("budget_amount")
    user_id = data.get("user_id")

    if not name or not user_id:
        return jsonify({"error": "name and user_id are required"}), 400

    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id
    ).first()

    if not category:
        return jsonify({"error": "Category not found"}), 404

    category.name = name
    category.budget_amount = budget_amount
    db.session.commit()

    return jsonify({
        "id": category.id,
        "name": category.name,
        "budget_amount": float(category.budget_amount) if category.budget_amount else None,
        "user_id": category.user_id
    }), 200

# Delete category
@category_api.route("/category/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id
    ).first()

    if not category:
        return jsonify({"error": "Category not found"}), 404

    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted"}), 200

# Get Budget by Category name
@category_api.route("/category/budget/<string:category_name>", methods=["GET"])
def get_budget_by_category_name(category_name):
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    category = Category.query.filter_by(
        name=category_name,
        user_id=user_id
    ).first()

    if not category:
        return jsonify({"error": "Category not found"}), 404

    return jsonify({
        "id": category.id,
        "name": category.name,
        "budget_amount": float(category.budget_amount) if category.budget_amount else None,
        "user_id": category.user_id
    }), 200