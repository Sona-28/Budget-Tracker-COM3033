import os
from flask import Flask
from dotenv import load_dotenv
from web_app.routes.main import main_blueprint
from web_app.routes.auth import auth_blueprint
from web_app.routes.transactions import transaction_blueprint
from web_app.routes.category import category_blueprint
from web_app.routes.analytics import analytics_blueprint

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

app.register_blueprint(main_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(transaction_blueprint)
app.register_blueprint(category_blueprint)
app.register_blueprint(analytics_blueprint)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
