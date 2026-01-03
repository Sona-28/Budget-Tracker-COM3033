import os
from flask import Flask
from dotenv import load_dotenv
from services.auth_service.extensions import db
from services.auth_service.models import init_db_if_missing

load_dotenv()

def create_app():
    app = Flask(__name__)

    # CONFIG
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('AUTH_DATABASE_URI')
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    
    db.init_app(app)
    init_db_if_missing(app)

    # from services.auth_service import models
    from services.auth_service.views import auth_api

    app.register_blueprint(auth_api)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(port=5001, debug=True)
