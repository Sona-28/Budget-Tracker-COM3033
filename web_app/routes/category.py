import os
import requests
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from web_app.forms.category_forms import CategoryForm

category_blueprint = Blueprint(
    "category",
    __name__,
    template_folder="../templates"
)

CATEGORY_SERVICE_URL = os.getenv("CATEGORY_SERVICE_URL", "http://localhost:5003")

# List Categories
@category_blueprint.route("/category")
def category():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for("auth.login"))

    try:
        resp = requests.get(
            f"{CATEGORY_SERVICE_URL}/category",
            params={"user_id": user_id},
            timeout=5
        )
    except requests.RequestException:
        flash("Category service unavailable.", "danger")
        return render_template("category/category.html", categories=[])

    if resp.status_code != 200:
        flash("Failed to load categories.", "danger")
        return render_template("category/category.html", categories=[])

    categories = resp.json()
    return render_template("category/category.html", categories=categories)


# Create Category
@category_blueprint.route("/category/create", methods=["GET", "POST"])
def create_category():
    form = CategoryForm()
    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = request.form.get("name")
        budget_amount = request.form.get("budget_amount")

        if not name:
            flash("Category name is required.", "danger")
            return redirect(url_for("category.create_category"))

        try:
            resp = requests.post(
                f"{CATEGORY_SERVICE_URL}/category",
                json={
                    "name": name,
                    "budget_amount": budget_amount,
                    "user_id": user_id
                },
                timeout=5
            )
        except requests.RequestException:
            flash("Category service unavailable.", "danger")
            return redirect(url_for("category.category"))

        if resp.status_code == 201:
            flash("Category created.", "success")
        else:
            flash("Failed to create category.", "danger")

        return redirect(url_for("category.category"))

    return render_template("category/create_category.html", form=form)


# Edit Category
@category_blueprint.route("/category/edit/<int:category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for("auth.login"))

    # POST – update category
    if request.method == "POST":
        name = request.form.get("name")
        budget_amount = request.form.get("budget_amount")
        if not name:
            flash("Category name is required.", "danger")
            return redirect(url_for("category.edit_category", category_id=category_id))


        try:
            resp = requests.put(
                f"{CATEGORY_SERVICE_URL}/category/{category_id}",
                json={
                    "name": name,
                    "budget_amount": budget_amount,
                    "user_id": user_id
                },
                timeout=5
            )
        except requests.RequestException:
            flash("Category service unavailable.", "danger")
            return redirect(url_for("category.edit_category", category_id=category_id))

        if resp.status_code != 200:
            flash("Failed to update category.", "danger")
            return redirect(url_for("category.edit_category", category_id=category_id))

        flash("Category updated successfully.", "success")
        return redirect(url_for("category.category"))

    # GET – load category
    try:
        resp = requests.get(
            f"{CATEGORY_SERVICE_URL}/category/{category_id}",
            params={"user_id": user_id},
            timeout=5
        )
    except requests.RequestException:
        flash("Category service unavailable.", "danger")
        return redirect(url_for("category.category"))

    if resp.status_code != 200:
        flash("Failed to load category.", "danger")
        return redirect(url_for("category.category"))

    category = resp.json()
    return render_template(
        "category/edit_category.html",
        category=category
    )


# Delete Category
@category_blueprint.route("/category/delete/<int:category_id>", methods=["POST"])
def delete_category(category_id):
    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for("auth.login"))

    try:
        requests.delete(
            f"{CATEGORY_SERVICE_URL}/category/{category_id}",
            params={"user_id": user_id},
            timeout=5
        )
        flash("Category deleted.", "success")
    except requests.RequestException:
        flash("Category service unavailable.", "danger")

    return redirect(url_for("category.category"))

