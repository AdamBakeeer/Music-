from app import app, db
from flask import render_template, flash
from .models import User, Artist, Song, SongArtist, Playlist, PlaylistSong, Chat
from flask import Flask, render_template, request, jsonify
from flask import jsonify, request, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from app.models import db, User, UserArtist, UserGenre, Artist, Genre
from flask import render_template, redirect, url_for, flash
from app.models import db, User, UserArtist, UserGenre, Artist, Genre
from werkzeug.security import generate_password_hash
from app.forms import SignupForm
from flask import Flask, render_template, redirect, url_for, flash, request, session
from werkzeug.security import check_password_hash
from app.models import User
from app.forms import LoginForm
from flask import Flask, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from app.models import db, User, UserArtist, UserGenre, Artist, Genre
from app.forms import SignupForm, DeleteAccountForm, PlaylistForm
from flask_wtf import FlaskForm
from flask import render_template, redirect, url_for, flash, request, session
from app.forms import PlaylistForm  # Adjust the import path as necessary
from flask import jsonify, request
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
import re  # For email validation




#Spotify credentials
client_id = "09e81b42d74d4504b5a4038da6625e60"
client_secret = "8bf09c6ca2344f178063eb6628829d4e"

# Last.fm API key
LASTFM_API_KEY = "404ef23228bb084db0c7f5114d94b8db"
BASE_URL = "http://ws.audioscrobbler.com/2.0/"


@app.route('/')
def index():
    playlists = []
    songs = []
    form = PlaylistForm()

    if 'user_id' in session:
        playlists = Playlist.query.filter_by(user_id=session['user_id']).all()
        songs = Song.query.all()
    return render_template('home.html', playlists=playlists, songs=songs, form=form)


@app.route('/sign', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    # Populate dropdowns dynamically
    form.artist1.choices = [(str(artist.artist_id), artist.artist_name) for artist in Artist.query.all()]
    form.artist2.choices = form.artist1.choices
    form.artist3.choices = form.artist1.choices
    form.genre1.choices = [(str(genre.genre_id), genre.genre_name) for genre in Genre.query.all()]
    form.genre2.choices = form.genre1.choices
    form.genre3.choices = form.genre1.choices

    if form.validate_on_submit():
        try:
            # Check for duplicate username and email
            existing_user = User.query.filter_by(username=form.username.data).first()
            existing_email = User.query.filter_by(email=form.email.data).first()

            if existing_user:
                flash("Username is already taken. Please choose a different username.", "danger")
                return render_template('signup.html', form=form)

            if existing_email:
                flash("Email is already registered. Please use a different email.", "danger")
                return render_template('signup.html', form=form)

            # Validate unique artist and genre selections
            artist_ids = [form.artist1.data, form.artist2.data, form.artist3.data]
            genre_ids = [form.genre1.data, form.genre2.data, form.genre3.data]

            if len(set(artist_ids)) != len(artist_ids):
                flash("Please select unique artists.", "danger")
                return render_template('signup.html', form=form)

            if len(set(genre_ids)) != len(genre_ids):
                flash("Please select unique genres.", "danger")
                return render_template('signup.html', form=form)

            # Extract form data
            first_name = form.first_name.data
            last_name = form.last_name.data
            email = form.email.data
            username = form.username.data
            password = generate_password_hash(form.password.data)

            # Save user to the database
            user = User(
                firstname=first_name,
                lastname=last_name,
                email=email,
                username=username,
                password_hash=password
            )
            db.session.add(user)
            db.session.commit()

            # Save artists
            for artist_id in set(artist_ids):  # Ensure no duplicates
                db.session.add(UserArtist(user_id=user.user_id, artist_id=artist_id))

            # Save genres
            for genre_id in set(genre_ids):  # Ensure no duplicates
                db.session.add(UserGenre(user_id=user.user_id, genre_id=genre_id))

            db.session.commit()

            # Save user ID in session and redirect
            session['user_id'] = user.user_id
            flash('Signup successful!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            print(f"Error during signup: {e}")
            flash('An error occurred during signup. Please try again.', 'danger')
    else:
        # Log form validation errors
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field.capitalize()}: {error}", "danger")
        else:
            flash("Please correct the errors in your form and try again.", "danger")

    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        identifier = form.identifier.data.strip()  # Get username/email
        password = form.password.data.strip()     # Get password

        # Determine if identifier is an email using regex
        is_email = re.match(r"[^@]+@[^@]+\.[^@]+", identifier)

        # Query user by email or username
        if is_email:
            user = User.query.filter_by(email=identifier).first()
        else:
            user = User.query.filter_by(username=identifier).first()

        # Authenticate user
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.user_id
            flash('You are now logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username/email or password. Please try again.', 'danger')

    # Render login form
    return render_template('login.html', form=form)
@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    user = User.query.get_or_404(user_id)
    if session.get('user_id') != user_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    # Create a base form for CSRF protection
    form = FlaskForm()
    
    # Fetch artists and genres for preferences
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

    # Update preferred artists
    artist_ids = [request.form['artist1'], request.form['artist2'], request.form['artist3']]
    UserArtist.query.filter_by(user_id=user.user_id).delete()
    for artist_id in artist_ids:
        db.session.add(UserArtist(user_id=user.user_id, artist_id=artist_id))

    # Update preferred genres
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



@app.route('/search_artist')
def search_artist():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])

    artists = Artist.query.filter(Artist.artist_name.ilike(f"%{query}%")).all()
    artist_list = [{"artist_id": artist.artist_id, "artist_name": artist.artist_name} for artist in artists]
    return jsonify(artist_list)


@app.route('/add_playlist', methods=['POST'])
def add_playlist():
    if 'user_id' not in session:
        flash("You need to log in to add a playlist.", "danger")
        return redirect(url_for('index'))

    playlist_name = request.form.get('playlist_name')
    song_ids = request.form.getlist('songs')

    if not playlist_name:
        flash("Playlist name is required.", "danger")
        return redirect(url_for('index'))

    try:
        # Create a new playlist
        new_playlist = Playlist(name=playlist_name, user_id=session['user_id'])
        db.session.add(new_playlist)
        db.session.commit()

        # Add selected songs to the playlist
        for song_id in song_ids:
            playlist_song = PlaylistSong(playlist_id=new_playlist.playlist_id, song_id=song_id)
            db.session.add(playlist_song)

        db.session.commit()
        flash("Playlist added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error adding playlist: {e}")
        flash("An error occurred while adding the playlist.", "danger")

    return redirect(url_for('index'))

@app.route('/search_song', methods=['GET'])
def search_song():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify([])

    matching_songs = Song.query.filter(Song.title.ilike(f"%{query}%")).all()
    return jsonify([{"song_id": song.song_id, "title": song.title} for song in matching_songs])

@app.route('/playlist/<int:playlist_id>', methods=['GET'])
def view_playlist(playlist_id):
    # Logic to view playlist details
    playlist = Playlist.query.get(playlist_id)
    if not playlist:
        flash('Playlist not found!', 'danger')
        return redirect(url_for('index'))
    return render_template('view_playlist.html', playlist=playlist)


@app.route('/search_song2', methods=['GET'])
def search_song2():
    query = request.args.get('query', '').strip()
    if not query:
        flash("Please enter a search query.", "danger")
        return redirect(url_for('index'))

    # Corrected to use Song.title
    songs = Song.query.filter(Song.title.ilike(f"%{query}%")).all()
    return render_template('search_results.html', songs=songs)

@app.route('/get_playlists', methods=['GET'])
def get_playlists():
    if 'user_id' not in session:
        return jsonify({"playlists": []})

    user_id = session['user_id']
    playlists = Playlist.query.filter_by(user_id=user_id).all()
    playlists_data = [{"id": p.id, "name": p.name} for p in playlists]
    return jsonify({"playlists": playlists_data})

@app.route('/add_song_to_playlist', methods=['POST'])
def add_song_to_playlist():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    song_id = data.get('song_id')
    playlist_id = data.get('playlist_id')

    playlist = Playlist.query.filter_by(id=playlist_id, user_id=session['user_id']).first()
    if not playlist:
        return jsonify({"error": "Invalid playlist"}), 403

    new_entry = PlaylistSong(playlist_id=playlist_id, song_id=song_id)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({"success": True})

