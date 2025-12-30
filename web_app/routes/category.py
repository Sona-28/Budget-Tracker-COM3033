import os
import requests
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    flash
)
from web_app.forms.category_forms import CategoryForm

category_blueprint = Blueprint(
    'category',
    __name__,
    template_folder='../templates'
)

CATEGORY_SERVICE_URL = os.getenv(
    "CATEGORY_SERVICE_URL",
    "http://localhost:5003"
)


def login_required():
    """Simple login guard (same style as navbar logic)."""
    if not session.get("user_id"):
        flash("Please log in to access categories.", "warning")
        return False
    return True


@category_blueprint.route('/category')
def category():
    if not login_required():
        return redirect(url_for('auth.login'))

    try:
        resp = requests.get(
            f"{CATEGORY_SERVICE_URL}/categories",
            params={"user_id": session["user_id"]},
            timeout=5
        )
    except requests.RequestException:
        flash("Category service is unavailable.", "danger")
        return render_template('category/category.html', categories=[])

    try:
        data = resp.json()
    except ValueError:
        data = []

    if resp.status_code == 200:
        return render_template(
            'category/category.html',
            categories=data
        )
    else:
        flash("Failed to load categories.", "danger")
        return render_template('category/category.html', categories=[])


@category_blueprint.route('/category/create', methods=["GET", "POST"])
def create_category():
    if not login_required():
        return redirect(url_for('auth.login'))

    form = CategoryForm()

    if form.validate_on_submit():
        budget = form.budget_amount.data
        if budget is not None:
            budget = float(budget)

        payload = {
            "user_id": session["user_id"],
            "name": form.name.data,
            "budget_amount": budget
        }

        try:
            resp = requests.post(
                f"{CATEGORY_SERVICE_URL}/categories",
                json=payload,
                timeout=5
            )
        except requests.RequestException:
            flash("Category service is unavailable.", "danger")
            return render_template(
                'category/create_category.html',
                form=form
            )

        try:
            data = resp.json()
        except ValueError:
            data = {}

        if resp.status_code == 201:
            flash("Category created successfully.", "success")
            return redirect(url_for('category.category'))
        else:
            error_msg = data.get("error", "Failed to create category.")
            flash(error_msg, "danger")

    return render_template(
        'category/create_category.html',
        form=form
    )

