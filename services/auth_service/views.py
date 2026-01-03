from flask import Blueprint, jsonify, request
from extensions import db
from models import User
import jwt
import os
from datetime import datetime, timedelta

auth_api = Blueprint('auth_api', __name__)

# -----------------------------------
# JWT configuration (must match other services)
# -----------------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60


@auth_api.get("/health")
def health():
    return jsonify(service="auth", status="ok")

@auth_api.get("/users/<int:user_id>")
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify(error="User not found"), 404

    return jsonify(
        id=user.id,
        firstname=user.firstname,
        lastname=user.lastname,
        email=user.email
    ), 200


@auth_api.post("/register")
def register():
    data = request.get_json() or {}

    required = ["firstname", "lastname", "email", "password"]
    if not all(data.get(f) for f in required):
        return jsonify(error="Missing required fields"), 400

    existing = User.query.filter_by(email=data["email"]).first()
    if existing:
        return jsonify(error="Email already registered"), 409

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

    # -----------------------------------
    # CREATE JWT
    # -----------------------------------
    payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES),
        "iat": datetime.utcnow()
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return jsonify(
        message="Login OK",
        user_id=user.id,
        access_token=token
    ), 200

