from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange


class CategoryForm(FlaskForm):
    name = StringField(
        "Category Name",
        validators=[DataRequired()]
    )

    budget_amount = DecimalField(
        "Monthly Budget",
        validators=[Optional(), NumberRange(min=0)],
        places=2
    )

    submit = SubmitField("Create Category")
