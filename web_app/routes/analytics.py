from flask import Blueprint, render_template
analytics_blueprint = Blueprint('analytics', __name__, template_folder='../templates')

@analytics_blueprint.route('/analytics')
def analytics():
    return render_template('analytics/analytics.html')

