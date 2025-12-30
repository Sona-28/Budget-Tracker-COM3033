from flask import Flask, request, jsonify
from extensions import db
from models import Category
import os
import requests


# -----------------------------------
# Auth service configuration
# -----------------------------------
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5001")


def validate_user(user_id: int) -> bool:
    """
    Validate user existence via Auth service.
    For coursework purposes, we validate by ensuring
    the Auth service is reachable.
    """
    try:
        resp = requests.get(f"{AUTH_SERVICE_URL}/health", timeout=3)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def create_app():
    app = Flask(__name__)

    # -----------------------------------
    # Database configuration
    # -----------------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://categories_user:strongpassword@localhost:3306/categoriesdb"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # -----------------------------------
    # Health check
    # -----------------------------------
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "service": "category",
            "status": "ok"
        }), 200

    # -----------------------------------
    # Create a category
    # -----------------------------------
    @app.route("/categories", methods=["POST"])
    def create_category():
        data = request.get_json()

        if not data or "user_id" not in data or "name" not in data:
            return jsonify({"error": "Missing required fields"}), 400

        if not validate_user(data["user_id"]):
            return jsonify({"error": "Invalid user"}), 401

        category = Category(
            user_id=data["user_id"],
            name=data["name"],
            budget_amount=data.get("budget_amount")
        )

        db.session.add(category)
        db.session.commit()

        return jsonify({
            "id": category.id,
            "user_id": category.user_id,
            "name": category.name,
            "budget_amount": float(category.budget_amount)
            if category.budget_amount else None
        }), 201

    # -----------------------------------
    # Get all categories for a user
    # -----------------------------------
    @app.route("/categories/<int:user_id>", methods=["GET"])
    def get_categories(user_id):
        if not validate_user(user_id):
            return jsonify({"error": "Invalid user"}), 401

        categories = Category.query.filter_by(user_id=user_id).all()

        return jsonify([
            {
                "id": c.id,
                "user_id": c.user_id,
                "name": c.name,
                "budget_amount": float(c.budget_amount)
                if c.budget_amount else None
            }
            for c in categories
        ]), 200

    # -----------------------------------
    # Get a single category (Transactions use-case)
    # -----------------------------------
    @app.route("/categories/<int:user_id>/<int:category_id>", methods=["GET"])
    def get_category(user_id, category_id):
        if not validate_user(user_id):
            return jsonify({"error": "Invalid user"}), 401

        category = Category.query.filter_by(
            id=category_id,
            user_id=user_id
        ).first()

        if not category:
            return jsonify({"error": "Category not found"}), 404

        return jsonify({
            "id": category.id,
            "user_id": category.user_id,
            "name": category.name,
            "budget_amount": float(category.budget_amount)
            if category.budget_amount else None
        }), 200

    # -----------------------------------
    # Seed default categories
    # -----------------------------------
    @app.route("/categories/seed", methods=["POST"])
    def seed_categories():
        data = request.get_json()

        if not data or "user_id" not in data:
            return jsonify({"error": "user_id required"}), 400

        user_id = data["user_id"]

        if not validate_user(user_id):
            return jsonify({"error": "Invalid user"}), 401

        default_categories = [
            ("Income", None),
            ("Food", 300.00),
            ("Transport", 150.00),
            ("Utilities", 200.00),
            ("Entertainment", 100.00),
            ("Health", 100.00),
        ]

        created = []

        for name, budget in default_categories:
            exists = Category.query.filter_by(
                user_id=user_id,
                name=name
            ).first()

            if not exists:
                category = Category(
                    user_id=user_id,
                    name=name,
                    budget_amount=budget
                )
                db.session.add(category)
                created.append(name)

        db.session.commit()

        return jsonify({
            "message": "Default categories seeded",
            "created": created
        }), 201

    return app


# -----------------------------------
# App entry point
# -----------------------------------
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5003, debug=True)

