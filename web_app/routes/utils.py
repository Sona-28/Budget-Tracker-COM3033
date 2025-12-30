from flask import flash, redirect, session, url_for


def require_login():
    if not session.get("user_id"):
        flash("Please log in to continue.", "warning")
        return redirect(url_for("auth.login"))
