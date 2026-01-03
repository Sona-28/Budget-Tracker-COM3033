import os
import requests
from flask import Blueprint, render_template, session, redirect, url_for, flash, request

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
        return redirect(url_for("auth.login"))

    response = requests.get(
        f"{CATEGORY_SERVICE_URL}/category",
        params={"user_id": user_id}
    )

    if response.status_code != 200:
        flash("Failed to fetch categories", "danger")
        return render_template("category/category.html", categories=[])

    categories_data = response.json()

    # 🔑 IMPORTANT: pass budget_amount through
    categories = []
    for c in categories_data:
        categories.append({
            "id": c["id"],
            "name": c["name"],
            "budget_amount": c.get("budget_amount")
        })

    return render_template(
        "category/category.html",
        categories=categories
    )



# Create Category
@category_blueprint.route("/category/create", methods=["GET", "POST"])
def create_category():
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

        payload = {
            "name": name,
     	    "budget_amount": (
                float(budget_amount) if budget_amount not in ("", None) else None
            )
        }

        try:
            resp = requests.post(
                f"{CATEGORY_SERVICE_URL}/category",
                json=payload,
                params={"user_id": user_id},
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

    return render_template("category/create_category.html")


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

        payload = {
            "name": name,
            "user_id": user_id,
            "budget_amount": (
                float(budget_amount) if budget_amount not in ("", None) else None
            )
        }


        try:
            resp = requests.put(
                f"{CATEGORY_SERVICE_URL}/category/{category_id}",
                json=payload,
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

    # GET - load category
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

