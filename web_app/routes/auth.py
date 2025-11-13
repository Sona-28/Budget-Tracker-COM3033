from flask import Blueprint, render_template
auth_blueprint = Blueprint('auth', __name__, template_folder='../templates')

@auth_blueprint.route('/register')
def register():
    return render_template('auth/register.html')

@auth_blueprint.route('/login')
def login():
    return render_template('auth/login.html')

@auth_blueprint.route('/account')
def account():
    return render_template('auth/account.html')
