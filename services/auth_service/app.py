import os
from flask import Flask
from dotenv import load_dotenv
from services.auth_service.extensions import db

load_dotenv()

def create_app():
    app = Flask(__name__)

    # CONFIG
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    auth_db_uri = os.getenv("AUTH_DATABASE_URI")
    if not auth_db_uri:
        auth_db_uri = "sqlite:///auth.db"  # fallback for local/dev
    
    app.config['SQLALCHEMY_DATABASE_URI'] = auth_db_uri
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from services.auth_service.models import User

    with app.app_context():
        db.create_all()

    # from services.auth_service import models
    from services.auth_service.views import auth_api

    app.register_blueprint(auth_api)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(port=5001, debug=True)
