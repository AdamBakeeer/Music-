from app import db

# User Table
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    preferred_artists = db.Column(db.String(200))  # Comma-separated artist IDs
    preferred_genres = db.Column(db.String(200))  # Comma-separated genres
    playlists = db.relationship('Playlist', backref='user', lazy='select')  # One-to-Many
    chats = db.relationship('Chat', backref='user', lazy='select')  # One-to-Many

# Artist Table
class Artist(db.Model):
    artist_id = db.Column(db.String(80), primary_key=True)  # Spotify Artist ID
    artist_name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    songs = db.relationship('SongArtist', back_populates='artist', lazy='select')  # Many-to-Many
    albums = db.relationship('Album', back_populates='artist', lazy='select')  # One-to-Many

# Album Table
class Album(db.Model):
    album_id = db.Column(db.String(80), primary_key=True)  # Spotify Album ID
    title = db.Column(db.String(200), nullable=False)
    release_date = db.Column(db.Date)
    artist_id = db.Column(db.String(80), db.ForeignKey('artist.artist_id'), nullable=False)
    artist = db.relationship('Artist', back_populates='albums')  # Many-to-One
    songs = db.relationship('Song', backref='album', lazy='select')  # One-to-Many

# Song Table
class Song(db.Model):
    song_id = db.Column(db.String(150), primary_key=True)  # Spotify Song ID
    title = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.Integer)
    genre = db.Column(db.String(80))
    album_id = db.Column(db.String(80), db.ForeignKey('album.album_id'))
    playlists = db.relationship('PlaylistSong', back_populates='song', lazy='select')  # Many-to-Many
    artists = db.relationship('SongArtist', back_populates='song', lazy='select')  # Many-to-Many

# SongArtist Linking Table (Many-to-Many: Songs ↔ Artists)
class SongArtist(db.Model):
    song_id = db.Column(db.String(80), db.ForeignKey('song.song_id'), primary_key=True)
    artist_id = db.Column(db.String(80), db.ForeignKey('artist.artist_id'), primary_key=True)
    song = db.relationship('Song', back_populates='artists')
    artist = db.relationship('Artist', back_populates='songs')

# Playlist Table
class Playlist(db.Model):
    playlist_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    songs = db.relationship('PlaylistSong', back_populates='playlist', lazy='select')  # Many-to-Many

# PlaylistSong Linking Table (Many-to-Many: Playlists ↔ Songs)
class PlaylistSong(db.Model):
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.playlist_id'), primary_key=True)
    song_id = db.Column(db.String(80), db.ForeignKey('song.song_id'), primary_key=True)
    playlist = db.relationship('Playlist', back_populates='songs')
    song = db.relationship('Song', back_populates='playlists')

# Chat Table
class Chat(db.Model):
    chat_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
