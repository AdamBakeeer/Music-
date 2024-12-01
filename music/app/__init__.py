from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel
from flask_admin import Admin
import os
from flask import Flask
app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)

def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')


app.config.from_object('config')
db = SQLAlchemy(app)
# Handles all migrations.
migrate = Migrate(app, db)

babel = Babel(app, locale_selector=get_locale)
admin = Admin(app,template_mode='bootstrap4')

from app import views, models

from flask import Flask,request, session

db = SQLAlchemy()
admin = Admin(name='Music Admin', template_mode='bootstrap4')

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
    app.config['SECRET_KEY'] = 'your_secret_key'
    
    # Initialize extensions
    db.init_app(app)
    admin.init_app(app)

    # Import and register models for admin
    from .models import User, Playlist, Artist, Album, Song, Chat
    from .admin import UserAdmin

    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(ModelView(Playlist, db.session))
    admin.add_view(ModelView(Artist, db.session))
    admin.add_view(ModelView(Album, db.session))
    admin.add_view(ModelView(Song, db.session))
    admin.add_view(ModelView(Chat, db.session))

    return app