from services.points_service.extensions import db

class PointsAccount(db.Model):
    __tablename__ = 'points'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)
    reason = db.Column(db.String(255), nullable=True)
    

    def __init__(self, user_id, points=0, reason=None):
        self.user_id = user_id
        self.points = points
        self.reason = reason

def init_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()