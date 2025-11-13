from flask import Blueprint, jsonify, request

auth_api = Blueprint('auth_api', __name__)


@auth_api.get("/health")
def health():
    return jsonify(service="auth", status="ok")


@auth_api.post("/register")
def register():
    return jsonify(message="register stub"), 201


@auth_api.post("/login")
def login():
    return jsonify(message="login stub", token="stub-token")


@auth_api.post("/forgot-password")
def forgot_password():
    return jsonify(message="forgot-password stub")
