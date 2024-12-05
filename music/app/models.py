from app import db


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), index=True, nullable=False)
    lastname = db.Column(db.String(100), index=True, nullable=False)
    username = db.Column(
        db.String(100), index=True, unique=True, nullable=False
    )
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    user_artists = db.relationship(
        'UserArtist', backref='user', cascade='all, delete-orphan'
    )
    user_genres = db.relationship(
        'UserGenre', backref='user', cascade='all, delete-orphan'
    )
    playlists = db.relationship(
        'Playlist', backref='user', cascade='all, delete-orphan'
    )
    chats = db.relationship(
        'Chat', backref='user', cascade='all, delete-orphan'
    )


class Artist(db.Model):
    artist_id = db.Column(db.String(80), primary_key=True)
    artist_name = db.Column(
        db.String(100), index=True, unique=True, nullable=False
    )
    listeners = db.Column(db.Integer, nullable=False, default=0)
    songs = db.relationship(
        'SongArtist', back_populates='artist', lazy='select'
    )
    preferred_by_users = db.relationship(
        'UserArtist', backref='artist', lazy='dynamic'
    )


class Song(db.Model):
    song_id = db.Column(db.String(150), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.Integer)
    genre = db.Column(db.String(80))
    artist_ids = db.Column(db.Text)
    playlists = db.relationship(
        'PlaylistSong', back_populates='song', lazy='select'
    )
    artists = db.relationship(
        'SongArtist', back_populates='song', lazy='select'
    )


class Genre(db.Model):
    genre_id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String(100), unique=True, nullable=False)
    preferred_by_users = db.relationship(
        'UserGenre', backref='genre', lazy='dynamic'
    )


class UserGenre(db.Model):
    __tablename__ = 'user_genre'
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.user_id'), primary_key=True
    )
    genre_id = db.Column(
        db.Integer, db.ForeignKey('genre.genre_id'), primary_key=True
    )


class SongArtist(db.Model):
    song_id = db.Column(
        db.String(80), db.ForeignKey('song.song_id'), primary_key=True
    )
    artist_id = db.Column(
        db.String(80), db.ForeignKey('artist.artist_id'), primary_key=True
    )
    song = db.relationship('Song', back_populates='artists')
    artist = db.relationship('Artist', back_populates='songs')


class Playlist(db.Model):
    playlist_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.user_id'), nullable=False
    )
    songs = db.relationship(
        'PlaylistSong', back_populates='playlist',
        lazy='select', cascade='all, delete-orphan'
    )


class PlaylistSong(db.Model):
    playlist_id = db.Column(
        db.Integer, db.ForeignKey('playlist.playlist_id'), primary_key=True
    )
    song_id = db.Column(
        db.String(80), db.ForeignKey('song.song_id'), primary_key=True
    )
    playlist = db.relationship('Playlist', back_populates='songs')
    song = db.relationship('Song', back_populates='playlists')


class UserArtist(db.Model):
    __tablename__ = 'user_artist'
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.user_id'), primary_key=True
    )
    artist_id = db.Column(
        db.String(80), db.ForeignKey('artist.artist_id'), primary_key=True
    )


class Chat(db.Model):
    chat_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.user_id'), nullable=False
    )
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
