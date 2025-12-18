from extensions import db
import bcrypt



class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    _password = db.Column("password", db.String(255), nullable=False) 
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=True)

    def __init__(self, email, password, firstname, lastname, phone=None):
        self.email = email
        self.firstname = firstname
        self.password = password
        self.lastname = lastname
        self.phone = phone

    @property
    def password(self):
        return self._password
    
    @password.setter
    def password(self, plaintext_password):
        hashed = bcrypt.hashpw(plaintext_password.encode('utf-8'), bcrypt.gensalt())
        self._password = hashed.decode("utf-8")

    def check_password(self, password_plain: str) -> bool:
        """Return True if the given plaintext password matches the stored hash."""
        return bcrypt.checkpw(
            password_plain.encode("utf-8"),
            self.password.encode("utf-8")
        )

def init_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()