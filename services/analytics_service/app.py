from flask import Flask
from dotenv import load_dotenv
from services.analytics_service.views import analytics_api


load_dotenv()

app = Flask(__name__)
app.register_blueprint(analytics_api)


if __name__ == "__main__":
    app.run(port=5004, debug=True)
