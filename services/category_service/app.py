from flask import Flask, request, jsonify
from extensions import db
from models import Category
import os
import jwt

# -----------------------------------
# JWT configuration (shared with auth service)
# -----------------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key")
JWT_ALGORITHM = "HS256"


def get_user_id_from_jwt(req):
    """
    Extract and validate JWT from Authorization header.
    Returns user_id if valid, otherwise None.
    """
    auth_header = req.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def create_app():
    app = Flask(__name__)

    # -----------------------------------
    # Database configuration
    # -----------------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://root:abhishekCOMM3033@localhost:3306/categoriesdb"
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
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "Missing required fields"}), 400

        category = Category(
            user_id=user_id,
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
            if category.budget_amount is not None else None
        }), 201

    # -----------------------------------
    # Get all categories for logged-in user
    # -----------------------------------
    @app.route("/categories", methods=["GET"])
    def get_categories():
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        categories = Category.query.filter_by(user_id=user_id).all()

        return jsonify([
            {
                "id": c.id,
                "user_id": c.user_id,
                "name": c.name,
                "budget_amount": float(c.budget_amount)
                if c.budget_amount is not None else None
            }
            for c in categories
        ]), 200

    # -----------------------------------
    # Get a single category
    # -----------------------------------
    @app.route("/categories/<int:category_id>", methods=["GET"])
    def get_category(category_id):
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

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
            if category.budget_amount is not None else None
        }), 200

    # -----------------------------------
    # Update a category
    # -----------------------------------
    @app.route("/categories/<int:category_id>", methods=["PUT"])
    def update_category(category_id):
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid payload"}), 400

        category = Category.query.filter_by(
            id=category_id,
            user_id=user_id
        ).first()

        if not category:
            return jsonify({"error": "Category not found"}), 404

        if "name" in data:
            category.name = data["name"]

        if "budget_amount" in data:
            category.budget_amount = data["budget_amount"]

        db.session.commit()

        return jsonify({
            "id": category.id,
            "user_id": category.user_id,
            "name": category.name,
            "budget_amount": float(category.budget_amount)
            if category.budget_amount is not None else None
        }), 200

    # -----------------------------------
    # Delete a category
    # -----------------------------------
    @app.route("/categories/<int:category_id>", methods=["DELETE"])
    def delete_category(category_id):
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        category = Category.query.filter_by(
            id=category_id,
            user_id=user_id
        ).first()

        if not category:
            return jsonify({"error": "Category not found"}), 404

        db.session.delete(category)
        db.session.commit()

        return jsonify({"message": "Category deleted"}), 200

    # -----------------------------------
    # Seed default categories
    # -----------------------------------
    @app.route("/categories/seed", methods=["POST"])
    def seed_categories():
        user_id = get_user_id_from_jwt(request)
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

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

