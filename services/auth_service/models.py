from services.auth_service.extensions import db
from sqlalchemy import inspect
import bcrypt


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    _password = db.Column("password", db.String(255), nullable=False) 
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=True)
    receive_email = db.Column(db.Boolean, default=True)

    def __init__(self, email, password, firstname, lastname, phone=None):
        self.email = email
        self.firstname = firstname
        self.password = password
        self.lastname = lastname
        self.phone = phone
        self.receive_email = True

    @property
    def password(self):
        return self._password
    
    @password.setter
    def password(self, plaintext_password):
        hashed = bcrypt.hashpw(plaintext_password.encode('utf-8'), bcrypt.gensalt())
        self._password = hashed.decode("utf-8")

    def check_password(self, password_plain: str) -> bool:
        return bcrypt.checkpw(
            password_plain.encode("utf-8"),
            self.password.encode("utf-8")
        )

def init_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()


def init_db_if_missing(app):
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table("users"):
            db.create_all()
