from flask import Flask, jsonify, request
from views import categories_api


app = Flask(__name__)
app.register_blueprint(categories_api)

if __name__ == "__main__":
    app.run(port=5003, debug=True)
