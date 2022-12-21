from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class NewUserForm(FlaskForm):
    """Form for adding users"""

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(
        min=6), EqualTo('confirm', message="Passwords must match")])
    confirm = PasswordField('Confirm Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login Form"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=6)])


class EditUserForm(FlaskForm):
    """Form for editing user data"""

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=6)])
    image_url = StringField('Image_URL')
    bio = TextAreaField('Bio', validators=[Length(max=250)])
