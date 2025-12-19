from flask import Flask
from views import transactions_api

app = Flask(__name__)
app.register_blueprint(transactions_api)

if __name__ == "__main__":
    app.run(port=5002, debug=True)
