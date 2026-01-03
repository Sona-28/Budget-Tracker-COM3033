from flask import Blueprint, jsonify
from models import Category
from extensions import db

category_blueprint = Blueprint("category", __name__)

@category_blueprint.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()

    return jsonify([
        {
            "id": c.id,
            "name": c.name
        }
        for c in categories
    ])

