from flask import Blueprint, request, jsonify
from models import PointsAccount
from extensions import db
import os
import requests

points_api = Blueprint("points_api", __name__)

@points_api.get("/health")
def health():
    return jsonify(service="points", status="ok")


@points_api.get("/points/<int:user_id>")
def get_total_points(user_id):
    total_points = db.session.query(
        db.func.coalesce(db.func.sum(PointsAccount.points), 0)
    ).filter(PointsAccount.user_id == user_id).scalar()

    return jsonify({
        "user_id": user_id,
        "total_points": total_points
    })

