from app import app, db, admin
from flask_admin.contrib.sqla import ModelView
from .models import User, Artist, Album, Song, SongArtist, Playlist, PlaylistSong, Chat

# Add Flask-Admin views for all tables
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Artist, db.session))
admin.add_view(ModelView(Album, db.session))
admin.add_view(ModelView(Song, db.session))
admin.add_view(ModelView(SongArtist, db.session))
admin.add_view(ModelView(Playlist, db.session))
admin.add_view(ModelView(PlaylistSong, db.session))
admin.add_view(ModelView(Chat, db.session))

@app.route('/')
def index():
    return "Hello World!!!"