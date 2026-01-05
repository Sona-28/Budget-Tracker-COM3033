from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from services.category_service.models import Category
from services.category_service.views import category_api
from services.category_service.extensions import db

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

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

from extensions import db
from routes import category_blueprint

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
database_uri = os.getenv("CATEGORY_DATABASE_URI")
if not database_uri:
    raise RuntimeError("CATEGORY_DATABASE_URI is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# Register routes
app.register_blueprint(category_blueprint)

# Health check
@app.route("/health", methods=["GET"])
def health():
    return {"status": "Category service is running"}, 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5003, debug=True)
