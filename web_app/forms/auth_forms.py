from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
import re


# Validating character check
def character_check(form, field):
    excluded_chars = "$ # @ < >  * ? ! ' ^ + % & / ( ) = { } [ ]"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(f"Character {char} is not allowed")


# Custom password validating
def validate_pass(form, password):
    p = re.compile("(?=.*[a-z])(?=.*[A-Z])(?=.*\d)")
    if not p.match(password.data):
        raise ValidationError("Should contain upper and lowercase character, and a digit")


# Custom phone digits validating
def validate_phone(form, phone):
    p = re.compile("[0-9]{4}\-[0-9]{3}\-[0-9]{4}")
    if not p.match(phone.data):
        raise ValidationError("Should have this format xxxx-xxx-xxxx")


# Validating the user registration form
class RegisterForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    firstname = StringField(validators=[DataRequired(), character_check])
    lastname = StringField(validators=[DataRequired(), character_check])
    phone = StringField(validators=[Optional(), validate_phone])
    password = PasswordField(validators=[DataRequired(), Length(min=6, max=12), validate_pass])
    confirm_password = PasswordField(validators=[DataRequired(), EqualTo('password', message='Both password fields must match')])
    submit = SubmitField()


# Validating the user login form
class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()