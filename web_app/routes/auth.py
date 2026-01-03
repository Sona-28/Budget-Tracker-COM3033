import os
import requests
from flask import Blueprint, render_template, redirect, request, session, url_for, flash
from web_app.forms.auth_forms import RegisterForm, LoginForm, ProfileForm, ChangePasswordForm

auth_blueprint = Blueprint('auth', __name__, template_folder='../templates')

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5001")
POINTS_SERVICE_URL = os.getenv("POINTS_SERVICE_URL", "http://localhost:5006")

@auth_blueprint.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        payload = {
            "firstname": form.firstname.data,
            "lastname": form.lastname.data,
            "email": form.email.data,
            "password": form.password.data,
            "phone": form.phone.data or None,
        }

        #print(payload)

        # Try to parse JSON response safely
        try:
            resp = requests.post(
                f"{AUTH_SERVICE_URL}/register",
                json=payload,
                timeout=5
            )
        except requests.RequestException:
            flash("Auth service is unavailable. Please try again later.", "danger")
            return render_template('auth/register.html', form=form)

        # Try to parse JSON response safely
        try:
            data = resp.json()
        except ValueError:
            data = {}

        if resp.status_code == 201:
            # Registration success
            flash("Registration successful. You can now log in.", "success")
            return redirect(url_for('auth.login'))
        else:
            # Something went wrong; show error from service if present
            error_msg = data.get("error", "Registration failed.")
            flash(error_msg, "danger")
            # Re-render the form with flashed message
            return render_template('auth/register.html', form=form)

    return render_template('auth/register.html', form=form)

@auth_blueprint.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        payload = {
            "email": form.email.data,
            "password": form.password.data,
        }

        try:
            resp = requests.post(
                f"{AUTH_SERVICE_URL}/login",
                json=payload,
                timeout=5
            )
        except requests.RequestException:
            flash("Auth service is unavailable. Please try again later.", "danger")
            return render_template('auth/login.html', form=form)

        try:
            data = resp.json()
        except ValueError:
            data = {}

        if resp.status_code == 200:
            session.clear()
            session["user_id"] = data.get("user_id")
            session["user_email"] = payload["email"]
            flash("Login successful.", "success")
            return redirect(url_for('analytics.analytics'))
        else:
            error_msg = data.get("error", "Login failed.")
            flash(error_msg, "danger")
            return render_template('auth/login.html', form=form)

    return render_template('auth/login.html', form=form)

@auth_blueprint.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for('main.main'))


@auth_blueprint.route('/account', methods=["GET", "POST"])
def account():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for("auth.login"))

    form = ProfileForm()
    password_form = ChangePasswordForm()

    try:
        resp = requests.get(f"{AUTH_SERVICE_URL}/users/{user_id}", timeout=5)
        print(resp.json())
        resp.raise_for_status()
        user = resp.json()
    except requests.RequestException:
        flash("Could not fetch profile info.", "danger")
        return redirect(url_for("auth.login"))

    user_email = user.get("email")

    # Fetch user's total points
    try:
        points_resp = requests.get(f"{POINTS_SERVICE_URL}/points/{user_id}", timeout=5)
        points_resp.raise_for_status()
        points_data = points_resp.json()
        total_points = points_data.get("total_points", 0)
    except requests.RequestException:
        total_points = 0  # Default to 0 if service unavailable

    if request.method == "GET":
        print("In GET method")
        form.firstname.data = user.get("firstname")
        form.lastname.data = user.get("lastname")
        form.phone.data = user.get("phone")
        form.receive_email.data = user.get("receive_email")


    if form.validate_on_submit():
        print("In POST method")
        payload = {
            "firstname": form.firstname.data,
            "lastname": form.lastname.data,
            "phone": form.phone.data,
            "receive_email": form.receive_email.data
        }
        try:
            update_resp = requests.put(
                f"{AUTH_SERVICE_URL}/users/{user_id}",
                json=payload,
                timeout=5
            )
            update_resp.raise_for_status()
        except requests.RequestException:
            flash("Failed to update profile. Please try again.", "danger")
            return render_template(
                "auth/account.html",
                form=form,
                user_email=user_email,
                password_form=password_form,
                total_points=total_points
            )

        flash("Profile updated successfully!", "success")

        form.firstname.data = payload["firstname"]
        form.lastname.data = payload["lastname"]
        form.phone.data = payload["phone"]
        form.receive_email.data = payload["receive_email"]

    return render_template(
        "auth/account.html",
        form=form,
        user_email=user_email,
        password_form=password_form,
        total_points=total_points
    )

@auth_blueprint.route('/change_password', methods=["POST"])
def change_password():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for("auth.login"))

    form = ChangePasswordForm()

    if not form.validate_on_submit():
        flash("Invalid password input.", "danger")
        return redirect(url_for("auth.account"))

    payload = {
        "user_id": user_id,
        "current_password": form.current_password.data,
        "new_password": form.new_password.data,
    }

    try:
        resp = requests.post(
            f"{AUTH_SERVICE_URL}/change-password",
            json=payload,
            timeout=5
        )
        resp.raise_for_status()
    except requests.RequestException:
        flash("Password update failed.", "danger")
        return redirect(url_for("auth.account"))

    flash("Password updated successfully.", "success")
    return redirect(url_for("auth.account"))