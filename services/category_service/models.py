from extensions import db

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)

    # user_id comes from Auth Service
    user_id = db.Column(db.Integer, nullable=False, index=True)

    name = db.Column(db.String(50), nullable=False)
    budget_amount = db.Column(db.Numeric(precision=10, scale=2), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="uq_user_category"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "budget_amount": float(self.budget_amount) if self.budget_amount else None
        }

