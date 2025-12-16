from flask import Blueprint, render_template

from web_app.routes.utils import require_login
analytics_blueprint = Blueprint('analytics', __name__, template_folder='../templates')

@analytics_blueprint.route('/analytics')
def analytics():
    guard = require_login()
    if guard: return guard
    return render_template('analytics/analytics.html')

