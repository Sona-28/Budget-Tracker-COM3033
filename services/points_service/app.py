from flask import Flask
from views import points_api
import os
from dotenv import load_dotenv
from extensions import db

load_dotenv()

def create_app():
    app = Flask(__name__)

    # CONFIG
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POINTS_DATABASE_URI')
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(points_api)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(port=5006, debug=True)
