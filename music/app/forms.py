from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf import FlaskForm
from wtforms import HiddenField


class SignupForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    artist1 = SelectField('Preferred Artist 1', choices=[], validators=[DataRequired()], coerce=str)
    artist2 = SelectField('Preferred Artist 2', choices=[], validators=[DataRequired()], coerce=str)
    artist3 = SelectField('Preferred Artist 3', choices=[], validators=[DataRequired()], coerce=str)
    genre1 = SelectField('Preferred Genre 1', choices=[], validators=[DataRequired()], coerce=str)
    genre2 = SelectField('Preferred Genre 2', choices=[], validators=[DataRequired()], coerce=str)
    genre3 = SelectField('Preferred Genre 3', choices=[], validators=[DataRequired()], coerce=str)
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    identifier = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class DeleteAccountForm(FlaskForm):
    hidden_token = HiddenField('CSRF Token')

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class PlaylistForm(FlaskForm):
    name = StringField('Playlist Name', validators=[DataRequired()])
    submit = SubmitField('Add Playlist')

class PlaylistForm(FlaskForm):
    playlist_name = StringField('Playlist Name', validators=[DataRequired()])
    songs = SelectMultipleField('Songs', validators=[DataRequired()], choices=[])
    submit = SubmitField('Add Playlist')