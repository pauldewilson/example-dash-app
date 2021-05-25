from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField


# login form
class LoginForm(FlaskForm):
    username = StringField("username")
    password = PasswordField("password")
