from flask import Flask, request, jsonify
from extensions import db
from models import Category


def create_app():
    app = Flask(__name__)

    # ------------------------
    # Database configuration
    # ------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://categories_user:strongpassword@localhost:3306/categoriesdb"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # ------------------------
    # Health check
    # ------------------------
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "service": "category",
            "status": "ok"
        }), 200

    # ------------------------
    # Create a category
    # ------------------------
    @app.route("/categories", methods=["POST"])
    def create_category():
        data = request.get_json()

        if not data or "user_id" not in data or "name" not in data:
            return jsonify({"error": "Missing required fields"}), 400

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
            "budget_amount": float(category.budget_amount) if category.budget_amount else None
        }), 201

    # ------------------------
    # Get categories by user
    # ------------------------
    @app.route("/categories/<int:user_id>", methods=["GET"])
    def get_categories(user_id):
        categories = Category.query.filter_by(user_id=user_id).all()

        return jsonify([
            {
                "id": c.id,
                "user_id": c.user_id,
                "name": c.name,
                "budget_amount": float(c.budget_amount) if c.budget_amount else None
            }
            for c in categories
        ]), 200

    return app


# ------------------------
# App entry point
# ------------------------
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5003, debug=True)

