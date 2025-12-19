from flask import Blueprint, render_template
category_blueprint = Blueprint('category', __name__, template_folder='../templates')

@category_blueprint.route('/category')
def category():
    return render_template('category/category.html')
