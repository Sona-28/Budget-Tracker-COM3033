from flask import Blueprint, jsonify, request
from services.auth_service.extensions import db
from services.auth_service.models import User

auth_api = Blueprint('auth_api', __name__)

@auth_api.get("/health")
def health():
    return jsonify(service="auth", status="ok")

@auth_api.post("/register")
def register():
    data = request.get_json() or {}

    required = ["firstname", "lastname", "email", "password"]
    if not all(data.get(f) for f in required):
        return jsonify(error="Missing required fields"), 400

    # query: does a user with this email already exist?
    existing = User.query.filter_by(email=data["email"]).first()

    if existing:
        return jsonify(error="Email already registered"), 409  # conflict


    user = User(
        firstname=data["firstname"],
        lastname=data["lastname"],
        email=data["email"],
        password=data["password"],
        phone=data.get("phone")
    )

    db.session.add(user)
    db.session.commit()

    return jsonify(message="User created"), 201


@auth_api.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify(error="Email and password required"), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify(error="Invalid credentials"), 401

    return jsonify(message="Login OK", user_id=user.id), 200

