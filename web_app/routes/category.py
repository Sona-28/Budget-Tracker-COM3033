import os
import requests
from flask import (
    Blueprint, render_template, redirect,
    url_for, session, flash
)
from web_app.forms.category_forms import CategoryForm

category_blueprint = Blueprint(
    "category", __name__, template_folder="../templates"
)

CATEGORY_SERVICE_URL = os.getenv(
    "CATEGORY_SERVICE_URL", "http://localhost:5003"
)

# -----------------------------------
# Helpers
# -----------------------------------
def auth_headers():
    token = session.get("access_token")
    print("JWT SENT TO CATEGORY:", token)
    if not token:
        return {}
    return {
        "Authorization": f"Bearer {token}"
    }


def login_required():
    if not session.get("user_id"):
        flash("Please log in.", "warning")
        return False
    return True


# -----------------------------------
# List categories
# -----------------------------------
@category_blueprint.route("/category")
def category():
    if not login_required():
        return redirect(url_for("auth.login"))

    categories = []

    try:
        resp = requests.get(
            f"{CATEGORY_SERVICE_URL}/categories",
            headers=auth_headers(),
            timeout=5
        )

        if resp.status_code == 200:
            categories = resp.json()
        else:
            flash(
                f"Failed to load categories ({resp.status_code}).",
                "danger"
            )

    except requests.RequestException:
        flash("Category service unavailable.", "danger")

    return render_template(
        "category/category.html",
        categories=categories
    )


# -----------------------------------
# Create category
# -----------------------------------
@category_blueprint.route("/category/create", methods=["GET", "POST"])
def create_category():
    if not login_required():
        return redirect(url_for("auth.login"))

    form = CategoryForm()

    if form.validate_on_submit():
        payload = {
            "name": form.name.data,
            "budget_amount": (
                float(form.budget_amount.data)
                if form.budget_amount.data is not None
                else None
            )
        }

        try:
            resp = requests.post(
                f"{CATEGORY_SERVICE_URL}/categories",
                json=payload,
                headers=auth_headers(),
                timeout=5
            )

            if resp.status_code != 201:
                error = resp.json().get("error", "Create failed.")
                flash(error, "danger")
                return render_template(
                    "category/create_category.html",
                    form=form
                )

        except requests.RequestException:
            flash("Category service unavailable.", "danger")
            return render_template(
                "category/create_category.html",
                form=form
            )

        flash("Category created.", "success")
        return redirect(url_for("category.category"))

    return render_template(
        "category/create_category.html",
        form=form
    )


# -----------------------------------
# Edit category
# -----------------------------------
@category_blueprint.route(
    "/category/<int:category_id>/edit",
    methods=["GET", "POST"]
)
def edit_category(category_id):
    if not login_required():
        return redirect(url_for("auth.login"))

    form = CategoryForm()

    if form.validate_on_submit():
        payload = {
            "name": form.name.data,
            "budget_amount": (
                float(form.budget_amount.data)
                if form.budget_amount.data is not None
                else None
            )
        }

        try:
            resp = requests.put(
                f"{CATEGORY_SERVICE_URL}/categories/{category_id}",
                json=payload,
                headers=auth_headers(),
                timeout=5
            )

            if resp.status_code != 200:
                flash("Failed to update category.", "danger")
                return render_template(
                    "category/edit_category.html",
                    form=form
                )

        except requests.RequestException:
            flash("Category service unavailable.", "danger")
            return render_template(
                "category/edit_category.html",
                form=form
            )

        flash("Category updated.", "success")
        return redirect(url_for("category.category"))

    return render_template(
        "category/edit_category.html",
        form=form
    )


# -----------------------------------
# Delete category
# -----------------------------------
@category_blueprint.route(
    "/category/<int:category_id>/delete",
    methods=["POST"]
)
def delete_category(category_id):
    if not login_required():
        return redirect(url_for("auth.login"))

    try:
        resp = requests.delete(
            f"{CATEGORY_SERVICE_URL}/categories/{category_id}",
            headers=auth_headers(),
            timeout=5
        )

        if resp.status_code == 200:
            flash("Category deleted.", "success")
        else:
            flash("Failed to delete category.", "danger")

    except requests.RequestException:
        flash("Category service unavailable.", "danger")

    return redirect(url_for("category.category"))

