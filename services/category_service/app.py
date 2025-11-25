from flask import Flask, render_template, request, redirect, url_for
from models import db, Category
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_default_categories()

    @app.route("/")
    def index():
        categories = Category.query.all()
        return render_template("index.html", categories=categories)

    @app.route("/add", methods=["POST"])
    def add_category():
        name = request.form["name"]
        if name.strip():
            new_cat = Category(name=name.strip())
            db.session.add(new_cat)
            db.session.commit()
        return redirect(url_for("index"))

    @app.route("/edit/<int:id>", methods=["GET", "POST"])
    def edit_category(id):
        category = Category.query.get_or_404(id)
        if request.method == "POST":
            category.name = request.form["name"]
            db.session.commit()
            return redirect(url_for("index"))
        return render_template("edit_category.html", category=category)

    @app.route("/delete/<int:id>")
    def delete_category(id):
        category = Category.query.get_or_404(id)
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for("index"))

    return app


def seed_default_categories():
    defaults = ["Income", "Food", "Transport", "Utilities", "Entertainment", "Health"]
    for name in defaults:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
