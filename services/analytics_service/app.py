from flask import Flask, jsonify, request
from views import analytics_api


app = Flask(__name__)
app.register_blueprint(analytics_api)


if __name__ == "__main__":
    app.run(port=5004, debug=True)
