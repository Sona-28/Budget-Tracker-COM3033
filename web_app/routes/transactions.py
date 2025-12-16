from flask import Blueprint, render_template
from web_app.routes.utils import require_login

transaction_blueprint = Blueprint('transaction', __name__, template_folder='../templates')

@transaction_blueprint.route('/transaction')
def transaction():
    guard = require_login()
    if guard: return guard
    return render_template('transaction/transaction.html')

# In the front end, we need to determine who is logged in, and session.get("user_id") does that.
# When sending that info to the backend, you send whatever info you wanted to from the front end,
# along with the user id, in the backend, you use the session id to find where that user is in the database,
# and whatever else.
# Use this to determine which user is making request
#user_id = session.get("user_id")
#payload = { **form_data, "user_id": user_id }
#resp = requests.post(f"{TRANSACTION_SERVICE_URL}/transactions", json=payload, timeout=5)