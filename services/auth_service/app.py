from flask import Flask
from views import auth_api


app = Flask(__name__)
app.register_blueprint(auth_api)

if __name__ == "__main__":
    app.run(port=5001, debug=True)
