from flask import Flask, jsonify, request
from views import points_api


app = Flask(__name__)
app.register_blueprint(points_api)

if __name__ == "__main__":
    app.run(port=5006, debug=True)
