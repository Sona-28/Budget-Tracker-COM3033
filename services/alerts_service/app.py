from flask import Flask
from services.alerts_service.views import alerts_api

def create_app():
    app = Flask(__name__)
    app.register_blueprint(alerts_api)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(port=5005, debug=True)
