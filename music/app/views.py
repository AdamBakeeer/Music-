from app import app, db
from flask import render_template, flash, session
from flask import request, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Artist, Song, Playlist
from app.models import PlaylistSong, UserArtist, UserGenre, Genre, SongArtist
from app.forms import SignupForm, LoginForm
from app.forms import PlaylistForm, CSRFProtectedForm, AddSongsForm
import re
from flask import g
import pylast


# Last.fm API key
LASTFM_API_KEY = "404ef23228bb084db0c7f5114d94b8db"
BASE_URL = "http://ws.audioscrobbler.com/2.0/"
network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=None)


def get_user_by_id(user_id):
    return User.query.filter_by(user_id=user_id).first()


@app.before_request
def before_request():
    session.permanent = False  # Make the session temporary
    user_id = session.get('user_id')
    if user_id:
        g.user = get_user_by_id(user_id)
    else:
        g.user = None


@app.route('/')
def index():
    playlists = []
    recommended_songs = []
    form = PlaylistForm()
    user = None
    top_tracks = get_weekly_top_tracks()

    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        playlists = Playlist.query.filter_by(user_id=session['user_id']).all()

        user_artists = UserArtist.query.filter_by(user_id=user.user_id).all()
        preferred_artists_ids = [user_artist.artist_id for user_artist in user_artists]

        for artist_id in preferred_artists_ids[:3]:
            song = Song.query.join(SongArtist).filter(
                SongArtist.artist_id == artist_id).first()

            if song:
                song_in_playlist = PlaylistSong.query.filter_by(
                    song_id=song.song_id).join(
                    Playlist).filter(Playlist.user_id == user.user_id).first()

                if not song_in_playlist:
                    recommended_songs.append(song)

    return render_template('home.html',playlists=playlists, form=form, user=user,top_tracks=top_tracks, recommended_songs=recommended_songs)


@app.route('/sign', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    form.artist1.choices = [(str(artist.artist_id), artist.artist_name) for artist in Artist.query.all()]
    form.artist2.choices = form.artist1.choices
    form.artist3.choices = form.artist1.choices
    form.genre1.choices = [(str(genre.genre_id), genre.genre_name) for genre in Genre.query.all()]
    form.genre2.choices = form.genre1.choices
    form.genre3.choices = form.genre1.choices

    if form.validate_on_submit():
        try:
            existing_user = User.query.filter_by(username=form.username.data).first()
            existing_email = User.query.filter_by(email=form.email.data).first()

            if existing_user:
                flash("Username is already taken. Please choose a different username.", "danger")
                return render_template('signup.html', form=form)

            if existing_email:
                flash("Email is already registered. Please use a different email.", "danger")
                return render_template('signup.html', form=form)

            artist_ids = [form.artist1.data, form.artist2.data, form.artist3.data]
            genre_ids = [form.genre1.data, form.genre2.data, form.genre3.data]

            if len(set(artist_ids)) != len(artist_ids):
                flash("Please select unique artists.", "danger")
                return render_template('signup.html', form=form)

            if len(set(genre_ids)) != len(genre_ids):
                flash("Please select unique genres.", "danger")
                return render_template('signup.html', form=form)

            user = User(
                firstname=form.first_name.data,
                lastname=form.last_name.data,
                email=form.email.data,
                username=form.username.data,
                password_hash=generate_password_hash(form.password.data)
            )
            db.session.add(user)
            db.session.commit()

            for artist_id in set(artist_ids):
                db.session.add(UserArtist(user_id=user.user_id, artist_id=artist_id))

            for genre_id in set(genre_ids):
                db.session.add(UserGenre(user_id=user.user_id, genre_id=genre_id))

            db.session.commit()

            session['user_id'] = user.user_id
            flash('Signup successful!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during signup. Please try again.', 'danger')
            return render_template('signup.html', form=form)
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        identifier = form.identifier.data.strip()
        password = form.password.data.strip()

        # Check if identifier is an email or username
        is_email = re.match(r"[^@]+@[^@]+\.[^@]+", identifier)
        user = None

        if is_email:
            user = User.query.filter_by(email=identifier).first()
        else:
            user = User.query.filter_by(username=identifier).first()

        # Validate user and password
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.user_id
            flash('You are now logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username/email or password. Please try again.', 'danger')

    return render_template('login.html', form=form)


@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    user = User.query.get_or_404(user_id)
    if session.get('user_id') != user_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    form = CSRFProtectedForm()
    artists = [(artist.artist_id, artist.artist_name) for artist in Artist.query.all()]
    genres = [(genre.genre_id, genre.genre_name) for genre in Genre.query.all()]

    return render_template('profile.html', user=user, form=form, artists=artists, genres=genres)


@app.route('/change_username', methods=['POST'])
def change_username():
    new_username = request.form['username']
    user = User.query.get(session['user_id'])
    user.username = new_username
    db.session.commit()
    flash('Username updated successfully!', 'success')
    return redirect(url_for('profile', user_id=user.user_id))


@app.route('/change_password', methods=['POST'])
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    user = User.query.get(session['user_id'])

    if not check_password_hash(user.password_hash, current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('profile', user_id=user.user_id))

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash('Password updated successfully!', 'success')
    return redirect(url_for('profile', user_id=user.user_id))


@app.route('/change_preferences', methods=['POST'])
def change_preferences():
    user = User.query.get(session['user_id'])

    artist_ids = [request.form['artist1'], request.form['artist2'], request.form['artist3']]
    UserArtist.query.filter_by(user_id=user.user_id).delete()
    for artist_id in artist_ids:
        db.session.add(UserArtist(user_id=user.user_id, artist_id=artist_id))

    genre_ids = [request.form['genre1'], request.form['genre2'], request.form['genre3']]
    UserGenre.query.filter_by(user_id=user.user_id).delete()
    for genre_id in genre_ids:
        db.session.add(UserGenre(user_id=user.user_id, genre_id=genre_id))

    db.session.commit()
    flash('Preferences updated successfully!', 'success')
    return redirect(url_for('profile', user_id=user.user_id))


@app.route('/delete_account', methods=['POST'])
def delete_account():
    user_id = session.get('user_id')
    if not user_id:
        flash('You are not logged in.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        session.pop('user_id', None)
        flash('Your account and all associated data have been deleted.', 'success')
        return redirect(url_for('index'))
    else:
        flash('User not found.', 'danger')
        return redirect(url_for('profile', user_id=user_id))


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))


@app.route('/search_song', methods=['GET'])
def search_song():
    query = request.args.get('query', '')
    if query:
        songs = Song.query.filter(Song.title.contains(query)).all()

        song_list = []
        for song in songs:
            artist_names = []
            song_artists = SongArtist.query.filter_by(song_id=song.song_id).all()
 
            for song_artist in song_artists:
                artist = Artist.query.get(song_artist.artist_id)
                if artist:
                    artist_names.append(artist.artist_name)

            song_list.append({
                'id': song.song_id,
                'title': song.title,
                'artists': artist_names
            })

        return jsonify({'songs': song_list})

    return render_template('search.html')


@app.route('/confirm_delete', methods=['GET', 'POST'])
def confirm_delete():
    if 'user_id' not in session:
        flash('You need to be logged in to delete your account.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get_or_404(user_id)

    form = CSRFProtectedForm()

    if form.validate_on_submit():
        db.session.delete(user)
        db.session.commit()
        session.clear()
        flash('Your account has been deleted.', 'success')
        return redirect(url_for('index'))

    return render_template('conf_del.html', user=user, form=form)


@app.route('/add_playlist', methods=['GET', 'POST'])
def add_playlist():
    if 'user_id' not in session:
        flash('You must be logged in to add songs to a playlist.', 'danger')
        return redirect(url_for('login'))

    form = AddSongsForm()
    form.song1.choices = [(song.song_id, song.title) for song in Song.query.limit(20).all()]
    form.song2.choices = form.song1.choices
    form.song3.choices = form.song1.choices
    form.song4.choices = form.song1.choices
    form.song5.choices = form.song1.choices

    if form.validate_on_submit():
        try:
            # Create a new playlist with the given name
            new_playlist = Playlist(
                name=form.playlist_name.data,
                user_id=session['user_id']  # Ensure the playlist is linked to the logged-in user
            )
            db.session.add(new_playlist)
            db.session.commit()

            # Get selected songs from the form
            song_ids = [form.song1.data, form.song2.data, form.song3.data, form.song4.data, form.song5.data]

            # Add each song to the playlist (ensure no duplicates)
            for song_id in set(song_ids):
                song = Song.query.get(song_id)
                if song:
                    playlist_song = PlaylistSong(playlist_id=new_playlist.playlist_id, song_id=song.song_id)
                    db.session.add(playlist_song)

            db.session.commit()
            flash('Playlist created and songs added successfully!', 'success')
            return redirect(url_for('index', playlist_id=new_playlist.playlist_id))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the playlist. Please try again.', 'danger')
            return render_template('add_playlist.html', form=form)

    return render_template('add_playlist.html', form=form)


@app.route('/view_playlist/<int:playlist_id>', methods=['GET', 'POST'])
def view_playlist(playlist_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch the playlist
    playlist = Playlist.query.get_or_404(playlist_id)

    # Check if the current user is the owner of the playlist
    if playlist.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'You are not the owner of this playlist'}), 403

    # Fetch the songs already in the playlist
    songs = Song.query.join(PlaylistSong).filter(PlaylistSong.playlist_id == playlist_id).all()

    # Fetch all available songs that are not in the playlist
    available_songs = Song.query.filter(~Song.song_id.in_([song.song_id for song in songs])).all()

    # Handle adding a song to the playlist
    if request.method == 'POST':
        song_id = request.form.get('song_id')  # Get the selected song's ID
        song = Song.query.get(song_id)
        if song:
            # Add the song to the playlist
            playlist_song = PlaylistSong(playlist_id=playlist.playlist_id, song_id=song.song_id)
            db.session.add(playlist_song)
            db.session.commit()
            flash("Song added to playlist!", "success")
            return redirect(url_for('view_playlist', playlist_id=playlist.playlist_id))  # Redirect to refresh the page

    return render_template('view_playlist.html', playlist=playlist, songs=songs, available_songs=available_songs)


@app.route('/remove_song', methods=['POST'])
def remove_song():
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    # Get JSON data from the request body
    data = request.get_json()
    song_id = data.get('song_id')
    playlist_id = data.get('playlist_id')

    # Find the song and playlist objects
    song = Song.query.get(song_id)
    playlist = Playlist.query.get(playlist_id)

    if not song or not playlist:
        return jsonify({'success': False, 'message': 'Song or Playlist not found'})

    # Find the relationship between the song and the playlist in the PlaylistSong table
    playlist_song = PlaylistSong.query.filter_by(song_id=song_id, playlist_id=playlist_id).first()

    if playlist_song:
        try:
            # Remove the song from the playlist
            db.session.delete(playlist_song)
            db.session.commit()
            return jsonify({'success': True})  # Return success if removal was successful
        except Exception as e:
            db.session.rollback()  # Rollback transaction on error
            print(f"Error removing song: {e}")
            return jsonify({'success': False, 'message': 'Error removing song'})
    else:
        return jsonify({'success': False, 'message': 'Song not found in playlist'})


def get_weekly_top_tracks():
    # Fetch the top tracks globally
    tracks = network.get_top_tracks()
    top_tracks = []

    # Collect track details (e.g., name, artist, URL, image)
    for track in tracks:
        top_tracks.append({
            'name': track.item.title,
            'artist': track.item.artist.name
        })

    return top_tracks


@app.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():
    if 'user_id' not in session:
        flash('You must be logged in to add songs to a playlist.', 'danger')
        return redirect(url_for('login'))

    song_id = request.form.get('song_id')
    playlist_id = request.form.get('playlist_id')

    # Fetch the song and playlist
    song = Song.query.get(song_id)
    playlist = Playlist.query.get(playlist_id)

    if song and playlist:
        # Add the song to the playlist
        playlist_song = PlaylistSong(playlist_id=playlist.playlist_id, song_id=song.song_id)
        db.session.add(playlist_song)
        db.session.commit()

        flash("Song added to playlist successfully!", "success")
    else:
        flash("Error: Song or Playlist not found.", "danger")

    return redirect(url_for('index'))


@app.route('/add_to_playlist2', methods=['POST'])
def add_to_playlist2():
    playlist_id = request.form.get('playlist_id')
    song_title = request.form.get('song_title')

    if not playlist_id or not song_title:
        flash('Missing playlist or song information.', 'danger')
        return redirect(url_for('index'))

    song = Song.query.filter_by(title=song_title).first()

    if not song:
        flash(f'Song "{song_title}" not found.', 'danger')
        return redirect(url_for('index'))

    # Find the playlist
    playlist = Playlist.query.get(playlist_id)

    if not playlist:
        flash('Playlist not found.', 'danger')
        return redirect(url_for('index'))

    # Check if the song is already in the playlist
    existing_entry = PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song.song_id).first()

    if existing_entry:
        flash('Song is already in this playlist.', 'info')
    else:
        # Add the song to the playlist
        new_entry = PlaylistSong(playlist_id=playlist_id, song_id=song.song_id)
        db.session.add(new_entry)
        db.session.commit()
        flash(f'Song "{song_title}" added to playlist!', 'success')

    return redirect(url_for('index'))


@app.route('/view_artist_songs/<artist_id>', methods=['GET'])
def view_artist_songs(artist_id):
    artist = Artist.query.get(artist_id)
    if artist:
        songs = Song.query.join(SongArtist).filter(SongArtist.artist_id == artist.artist_id).all()
        return render_template('artist_songs.html', artist=artist, songs=songs)
    else:
        return "Artist not found", 404


@app.route('/search_artist', methods=['GET'])
def search_artist():
    query = request.args.get('query', '')
    if query:
        artists = Artist.query.filter(Artist.artist_name.contains(query)).all()

        artist_list = []
        for artist in artists:
            artist_list.append({
                'artist_id': artist.artist_id,
                'artist_name': artist.artist_name
            })

        return jsonify(artist_list)

    return render_template('search_artist.html')
