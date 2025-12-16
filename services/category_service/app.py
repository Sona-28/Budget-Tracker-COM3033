from flask import Flask, render_template, request, redirect, url_for
from models import db, Category
from config import Config
from decimal import Decimal
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)

    @app.route("/")
    def index():
        categories = Category.query.all()
        return render_template("index.html", categories=categories)

    @app.route("/add", methods=["POST"])
    def add_category():
        name = request.form["name"]
        budget_amount = request.form.get("budget_amount")

        if name.strip():
            new_cat = Category(
                name=name.strip(),
                budget_amount=Decimal(budget_amount) if budget_amount else None
            )
            db.session.add(new_cat)
            db.session.commit()
        return redirect(url_for("index"))

    @app.route("/edit/<int:id>", methods=["GET", "POST"])
    def edit_category(id):
        category = Category.query.get_or_404(id)

        if request.method == "POST":
            category.name = request.form["name"]
            budget_amount = request.form.get("budget_amount")
            category.budget_amount = Decimal(budget_amount) if budget_amount else None

            db.session.commit()
            return redirect(url_for("index"))

        return render_template("edit_category.html", category=category)

    @app.route("/delete/<int:id>")
    def delete_category(id):
        category = Category.query.get_or_404(id)
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for("index"))

    @app.cli.command("seed")
    def seed():
        """Seed default categories."""
        seed_default_categories()

    return app

def seed_default_categories():
    defaults = [
        "Income",
        "Food",
        "Transport",
        "Utilities",
        "Entertainment",
        "Health"
    ]

    for name in defaults:
        exists = Category.query.filter_by(name=name).first()
        if not exists:
            db.session.add(Category(name=name, budget_amount=None))

    db.session.commit()

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
