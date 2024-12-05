from app import app, db
from flask import render_template, flash, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Artist, Song, Playlist, PlaylistSong, UserArtist, UserGenre, Genre, SongArtist, Chat
from app.forms import SignupForm, LoginForm, PlaylistForm, DeleteAccountForm, CSRFProtectedForm, AddSongsForm, SongRemoveForm
import re
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from flask import g
import pyl
# Last.fm API key
LASTFM_API_KEY = "404ef23228bb084db0c7f5114d94b8db"
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

def get_user_by_id(user_id):
    return User.query.filter_by(user_id=user_id).first()

@app.before_request
def before_request():
    # Assuming you store the user ID in the session after login
    user_id = session.get('user_id')  # Retrieve user_id from session
    if user_id:
        # Query the database or API to get the user object (example)
        g.user = get_user_by_id(user_id)  # Replace this with your actual method to get user data
    else:
        g.user = None


@app.route('/')
def index():
    playlists = []
    recommended_songs = []  # Initialize recommended_songs as an empty list
    form = PlaylistForm()
    user = None
    top_tracks = get_weekly_top_tracks()  # Assume this function fetches the top tracks of the week

    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        playlists = Playlist.query.filter_by(user_id=session['user_id']).all()

        # Get user's preferred artists from the UserArtist table
        user_artists = UserArtist.query.filter_by(user_id=user.user_id).all()
        preferred_artists_ids = [user_artist.artist_id for user_artist in user_artists]

        # For each artist, get a song associated with them
        for artist_id in preferred_artists_ids[:3]:  # Limit to 3 artists
            # Fetch one song for the current artist
            song = Song.query.join(SongArtist).filter(SongArtist.artist_id == artist_id).first()

            if song:
                # Check if the song is already in any of the user's playlists
                song_in_playlist = PlaylistSong.query.filter_by(song_id=song.song_id).join(Playlist).filter(Playlist.user_id == user.user_id).first()

                if not song_in_playlist:  # If the song is not in the playlist
                    recommended_songs.append(song)

    return render_template(
        'home.html', 
        playlists=playlists, 
        form=form, 
        user=user, 
        top_tracks=top_tracks, 
        recommended_songs=recommended_songs
    )

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

        is_email = re.match(r"[^@]+@[^@]+\.[^@]+", identifier)
        user = User.query.filter_by(email=identifier).first() if is_email else User.query.filter_by(username=identifier).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.user_id
            flash('You are now logged in!', 'success')  # Flash a success message on successful login
            return redirect(url_for('index'))
        else:
            flash('Invalid username/email or password. Please try again.', 'danger')  # Flash a danger message on login failure

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
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify([])

    matching_songs = Song.query.filter(Song.title.ilike(f"%{query}%")).all()
    return jsonify([{"song_id": song.song_id, "title": song.title} for song in matching_songs])



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
        return redirect(url_for('login'))  # Redirect to login page if user is not logged in

    # Fetch the playlist
    playlist = Playlist.query.get_or_404(playlist_id)
    
    # Check if the current user is the owner of the playlist
    if playlist.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'You are not the owner of this playlist'}), 403

    # Fetch the songs in the playlist
    songs = Song.query.join(PlaylistSong).filter(PlaylistSong.playlist_id == playlist_id).all()

    # Create the form for CSRF protection
    form = SongRemoveForm()  # You can create a form to handle CSRF token if necessary

    return render_template('view_playlist.html', playlist=playlist, songs=songs, form=form)


@app.route('/remove_song', methods=['POST'])
def remove_song():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    song_id = request.form.get('song_id')
    playlist_id = request.form.get('playlist_id')
    
    # Find the song and playlist
    song = Song.query.get(song_id)
    playlist = Playlist.query.get(playlist_id)
    
    if not song or not playlist:
        return jsonify({'success': False, 'message': 'Song or Playlist not found'})

    # Find the relationship between the song and the playlist
    playlist_song = PlaylistSong.query.filter_by(song_id=song_id, playlist_id=playlist_id).first()
    
    if playlist_song:
        db.session.delete(playlist_song)
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Song not in playlist'})
    
@app.route('/search', methods=['GET', 'POST'])
def search():

    if request.method == 'POST':
        search_query = request.form.get('search_query')
        songs = Song.query.filter(Song.title.contains(search_query)).all()
        song_list = [{
            'id': song.id,
            'title': song.title,
            'artist': song.artist.name,  # Assuming 'artist' is a relation
            'cover_url': song.cover_url  # Assuming a 'cover_url' field for the song cover image
        } for song in songs]
        return jsonify({'songs': song_list})

    return render_template('search.html')

  # You can change 'home' to the desired route

@app.route('/artist_songs/<int:artist_id>')
def artist_songs(artist_id):
    # Assuming you have a model named Song related to Artist
    artist = Artist.query.get_or_404(artist_id)
    songs = Song.query.filter_by(artist_id=artist.id).all()
    return render_template('artist_songs.html', artist=artist, songs=songs)

@app.route('/search_artist')
def search_artist():
    query = request.args.get('query', '')
    
    if query:
        # Assuming you have a model named Artist
        artists = Artist.query.filter(Artist.name.ilike(f"%{query}%")).all()
        artist_data = [{"id": artist.id, "name": artist.name} for artist in artists]
        return jsonify(artist_data)
    else:
        return jsonify([]) 


# Last.fm API credentials
LASTFM_API_KEY = "404ef23228bb084db0c7f5114d94b8db"
network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=None)

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

@app.route('/ask_chatbot', methods=['POST'])
def ask_chatbot():
    user_message = request.form.get('message')
    user_id = g.user.user_id  # Assuming the user is logged in and g.user contains user data
    
    # Use OpenAI API to get the response
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can replace with other models if necessary
            prompt=f"Answer this music-related question: {user_message}",
            max_tokens=150
        )
        answer = response.choices[0].text.strip()

        # Store the question and response in the Chat model
        chat = Chat(user_id=user_id, message=user_message, response=answer)
        db.session.add(chat)
        db.session.commit()

    except Exception as e:
        answer = "Sorry, something went wrong. Please try again."

    return jsonify({'answer': answer})