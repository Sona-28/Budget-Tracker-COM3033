import os
from flask import Flask
from dotenv import load_dotenv

from extensions import db
from views import auth_api

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "AUTH_DATABASE_URI",
        "mysql+pymysql://auth_user:strongpassword@localhost:3306/authdb"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True

    db.init_app(app)

    with app.app_context():
        import models

    from views import auth_api
    app.register_blueprint(auth_api)

    @app.route("/health")
    def health():
        return {"status": "auth service healthy"}, 200

    return app

app = create_app()

if __name__ == "__main__":
    app.run(port=5001, debug=True)

