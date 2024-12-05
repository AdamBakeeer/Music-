from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField, SelectMultipleField,
    SubmitField, HiddenField
)
from wtforms.validators import DataRequired, Email, Length


class SignupForm(FlaskForm):
    first_name = StringField(
        'First Name', validators=[DataRequired(), Length(max=50)]
    )
    last_name = StringField(
        'Last Name', validators=[DataRequired(), Length(max=50)]
    )
    email = StringField(
        'Email', validators=[DataRequired(), Email()]
    )
    username = StringField(
        'Username', validators=[DataRequired(), Length(max=50)]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(), Length(min=6)]
    )
    artist1 = SelectField(
        'Preferred Artist 1', choices=[], validators=[DataRequired()],
        coerce=str
    )
    artist2 = SelectField(
        'Preferred Artist 2', choices=[], validators=[DataRequired()],
        coerce=str
    )
    artist3 = SelectField(
        'Preferred Artist 3', choices=[], validators=[DataRequired()],
        coerce=str
    )
    genre1 = SelectField(
        'Preferred Genre 1', choices=[], validators=[DataRequired()],
        coerce=str
    )
    genre2 = SelectField(
        'Preferred Genre 2', choices=[], validators=[DataRequired()],
        coerce=str
    )
    genre3 = SelectField(
        'Preferred Genre 3', choices=[], validators=[DataRequired()],
        coerce=str
    )
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    identifier = StringField(
        'Username or Email', validators=[DataRequired()]
    )
    password = PasswordField(
        'Password', validators=[DataRequired()]
    )
    submit = SubmitField('Login')


class DeleteAccountForm(FlaskForm):
    hidden_token = HiddenField('CSRF Token')


class PlaylistForm(FlaskForm):
    playlist_name = StringField(
        'Playlist Name', validators=[DataRequired()]
    )
    song_ids = SelectMultipleField(
        'Select Songs', coerce=int, validators=[DataRequired()]
    )
    submit = SubmitField('Create Playlist')


class CSRFProtectedForm(FlaskForm):
    pass


class AddSongsForm(FlaskForm):
    playlist_name = StringField(
        'Playlist Name', validators=[DataRequired()]
    )
    song1 = SelectField(
        'Song 1', validators=[DataRequired()]
    )
    song2 = SelectField(
        'Song 2', validators=[DataRequired()]
    )
    song3 = SelectField(
        'Song 3', validators=[DataRequired()]
    )
    song4 = SelectField(
        'Song 4', validators=[DataRequired()]
    )
    song5 = SelectField(
        'Song 5', validators=[DataRequired()]
    )


class SongRemoveForm(FlaskForm):
    song_id = HiddenField(
        'Song ID', validators=[DataRequired()]
    )
    playlist_id = HiddenField(
        'Playlist ID', validators=[DataRequired()]
    )


class ChatForm(FlaskForm):
    message = StringField(
        'Message', validators=[DataRequired()]
    )
