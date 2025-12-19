from flask import Flask, jsonify, request
from views import alerts_api


app = Flask(__name__)
app.register_blueprint(alerts_api)


if __name__ == "__main__":
    app.run(port=5005, debug=True)
