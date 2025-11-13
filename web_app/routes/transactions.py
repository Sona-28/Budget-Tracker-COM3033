from flask import Blueprint, render_template
transaction_blueprint = Blueprint('transaction', __name__, template_folder='../templates')

@transaction_blueprint.route('/transaction')
def transaction():
    return render_template('transaction/transaction.html')
