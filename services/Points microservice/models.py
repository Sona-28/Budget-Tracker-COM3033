from extensions import db
from datetime import datetime


# Stores current total points per user
class PointsAccount(db.Model):
    __tablename__ = "points_account"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    total_points = db.Column(db.Integer, default=0)


# Stores history of points earned / deducted
class RewardLog(db.Model):
    __tablename__ = "reward_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

