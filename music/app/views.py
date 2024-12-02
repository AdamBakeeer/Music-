from app import app, db
from flask import render_template, flash
from .models import User, Artist, Song, SongArtist, Playlist, PlaylistSong, Chat
from flask import Flask, render_template, request, jsonify

#Spotify credentials
client_id = "09e81b42d74d4504b5a4038da6625e60"
client_secret = "8bf09c6ca2344f178063eb6628829d4e"

# Last.fm API key
LASTFM_API_KEY = "404ef23228bb084db0c7f5114d94b8db"
BASE_URL = "http://ws.audioscrobbler.com/2.0/"


@app.route('/')
def index():
    return render_template("base.html") 

@app.route('/sign')
def signup():
    return render_template("signup.html") 

@app.route('/search_artists', methods=['GET'])
def search_artists():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify([])  # Return an empty list if no query is provided
    
    # Query your database for artists that match the input
    matching_artists = Artist.query.filter(Artist.name.ilike(f"{query}%")).all()
    result = [{'id': artist.id, 'name': artist.name} for artist in matching_artists]
    
    return jsonify(result)