import os

import requests
from flask import Blueprint, render_template, redirect, session, url_for, flash
from web_app.forms.auth_forms import RegisterForm, LoginForm

auth_blueprint = Blueprint('auth', __name__, template_folder='../templates')

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5001")

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

        print(payload)

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

        # Call auth service
        try:
            resp = requests.post(
                f"{AUTH_SERVICE_URL}/login",
                json=payload,
                timeout=5
            )
        except requests.RequestException:
            flash(
                "Auth service is unavailable. Please try again later.",
                "danger"
            )
            return render_template('auth/login.html', form=form)

        # Safely parse JSON
        try:
            data = resp.json()
        except ValueError:
            data = {}

        if resp.status_code == 200:
            # Clear any old session data
            session.clear()

            # Store user info
            session["user_id"] = data.get("user_id")
            session["user_email"] = payload["email"]

            # Store JWT (support common key names)
            session["access_token"] = (
                data.get("access_token")
                or data.get("token")
                or data.get("jwt")
            )

            # Safety check
            if not session.get("access_token"):
                flash(
                    "Login succeeded but no access token was returned.",
                    "danger"
                )
                return render_template('auth/login.html', form=form)

            flash("Login successful.", "success")
            return redirect(url_for('auth.account'))

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


@auth_blueprint.route('/account')
def account():
    return render_template('auth/account.html')
