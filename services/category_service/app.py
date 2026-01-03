from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load .env from project root
load_dotenv()

app = Flask(__name__)

# Database configuration
database_uri = os.getenv("CATEGORY_DATABASE_URI")
if not database_uri:
    raise RuntimeError("CATEGORY_DATABASE_URI is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    budget_amount = db.Column(db.Numeric(precision=10, scale=2), nullable=True)

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
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Category service is running"}), 200

# Get all categories (with default seeding)
@app.route("/category", methods=["GET"])
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
@app.route("/category/<int:category_id>", methods=["GET"])
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
@app.route("/category", methods=["POST"])
def create_category():
    data = request.json
    name = data.get("name")
    budget_amount = data.get("budget_amount")
    user_id = data.get("user_id")
    print(data)
    if not name or not user_id:
        return jsonify({"error": "name and user_id are required"}), 400

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
@app.route("/category/<int:category_id>", methods=["PUT"])
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
@app.route("/category/<int:category_id>", methods=["DELETE"])
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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5003, debug=True)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

from extensions import db
from routes import category_blueprint

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
database_uri = os.getenv("CATEGORY_DATABASE_URI")
if not database_uri:
    raise RuntimeError("CATEGORY_DATABASE_URI is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# Register routes
app.register_blueprint(category_blueprint)

# Health check
@app.route("/health", methods=["GET"])
def health():
    return {"status": "Category service is running"}, 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5003, debug=True)
