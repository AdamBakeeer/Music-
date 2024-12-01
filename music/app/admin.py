from flask_admin.contrib.sqla import ModelView
from wtforms.fields import TextAreaField
from flask_admin.form import TextAreaField

class UserAdmin(ModelView):
    form_overrides = {
    'preferred_artists': TextAreaField,  # Use TextArea for comma-separated fields
    'preferred_genres': TextAreaField,
    }
    column_searchable_list = ['username', 'email']
    column_filters = ['username', 'email']
    form_excluded_columns = ['password_hash']
    

class ArtistAdmin(ModelView):
    column_searchable_list = ['artist_name']
