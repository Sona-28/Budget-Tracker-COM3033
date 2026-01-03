from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from models import Category
from views import category_api
from extensions import db

# Load .env from project root
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # CONFIG
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('CATEGORY_DATABASE_URI')
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Initialize the database
    with app.app_context():
        db.create_all()

    app.register_blueprint(category_api)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(port=5003, debug=True)

