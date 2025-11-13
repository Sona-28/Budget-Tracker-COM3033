from flask import Blueprint, jsonify, request

transactions_api = Blueprint('transactions_api', __name__)


@transactions_api.get("/health")
def health():
    return jsonify(service="transaction", status="ok")


@transactions_api.get("/transactions")
def list_transactions():
    return jsonify(items=[])


@transactions_api.post("/transactions")
def create_transaction():
    return jsonify(message="create stub"), 201


@transactions_api.put("/transactions/<tid>")
def update_transaction(tid):
    return jsonify(message=f"update {tid} stub")


@transactions_api.delete("/transactions/<tid>")
def delete_transaction(tid):
    return jsonify(message=f"delete {tid} stub")
