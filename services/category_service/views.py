from flask import Blueprint, jsonify, request

categories_api = Blueprint('categories_api', __name__)


@categories_api.get("/health")
def health():
    return jsonify(service="category", status="ok")


@categories_api.get("/categories")
def list_categories():
    return jsonify(items=[])


@categories_api.post("/categories")
def create_category():
    # expected JSON: name, budget(optional)
    return jsonify(message="create category stub"), 201


@categories_api.put("/categories/<cid>")
def update_category(cid):
    return jsonify(message=f"update {cid} stub")


@categories_api.delete("/categories/<cid>")
def delete_category(cid):
    return jsonify(message=f"delete {cid} stub")
