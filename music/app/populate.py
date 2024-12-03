from app import app, db
from  app.models import Artist, Song, SongArtist, Genre
import requests

# Last.fm API configuration
LASTFM_API_KEY = "404ef23228bb084db0c7f5114d94b8db"
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

def fetch_top_artists(limit=50):
    """
    Fetch the top global artists from Last.fm.
    """
    params = {
        "method": "chart.gettopartists",
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": limit
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        artists = response.json().get("artists", {}).get("artist", [])
        return [
            {
                "artist_id": artist["mbid"] or artist["name"].replace(" ", "_").lower(),
                "artist_name": artist["name"],
                "listeners": int(artist["listeners"])
            }
            for artist in artists
        ]
    else:
        print(f"Error fetching artists: {response.status_code}")
        return []

def fetch_top_tracks_for_artist_with_genres(artist_name, limit=20):
    """
    Fetch the top tracks for a specific artist from Last.fm, including genres for each track,
    and save genres to the Genre table.
    """
    # Step 1: Fetch top tracks
    params = {
        "method": "artist.gettoptracks",
        "artist": artist_name,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": limit
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        tracks = response.json().get("toptracks", {}).get("track", [])
        
        # Step 2: Fetch genres for each track
        enriched_tracks = []
        for track in tracks:
            track_name = track.get("name")
            if not track_name:  # Skip tracks without a name
                continue
            
            # Generate a unique identifier for the track
            song_id = track.get("mbid") or f"{artist_name.replace(' ', '_').lower()}_{track_name.replace(' ', '_').lower()}"

            # Fetch genres using the track.getTopTags endpoint
            genres = fetch_genres_for_track(artist_name, track_name)
            
            # Save genres to the database
            save_genres_to_db(genres)

            enriched_tracks.append({
                "song_id": song_id,
                "title": track_name,
                "genres": genres  # List of genres for this track
            })
        return enriched_tracks
    else:
        print(f"Error fetching tracks for {artist_name}: {response.status_code} - {response.text}")
        return []

def fetch_genres_for_track(artist_name, track_name):
    """
    Fetch the genres (tags) for a specific track from Last.fm.
    """
    params = {
        "method": "track.gettoptags",
        "artist": artist_name,
        "track": track_name,
        "api_key": LASTFM_API_KEY,
        "format": "json"
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        tags = response.json().get("toptags", {}).get("tag", [])
        # Return a list of genre names
        return [tag.get("name") for tag in tags]
    else:
        print(f"Error fetching genres for track {track_name}: {response.status_code} - {response.text}")
        return []

def save_genres_to_db(genres):
    """
    Save genres to the Genre table in the database, ensuring no duplicates.
    """
    for genre_name in genres:
        # Check if the genre already exists in the database
        existing_genre = Genre.query.filter_by(genre_name=genre_name).first()
        if not existing_genre:
            # Insert new genre
            new_genre = Genre(genre_name=genre_name)
            db.session.add(new_genre)
    db.session.commit()

def populate_database():
    """
    Populate the database with top artists, their tracks, and genres.
    """
    print("Fetching top artists...")
    top_artists = fetch_top_artists(limit=50)

    for artist in top_artists:
        print(f"Processing artist: {artist['artist_name']} ({artist['artist_id']})")
        
        # Save artist to the database
        existing_artist = Artist.query.filter_by(artist_id=artist["artist_id"]).first()
        if not existing_artist:
            new_artist = Artist(
                artist_id=artist["artist_id"],
                artist_name=artist["artist_name"],
                listeners=artist["listeners"]
            )
            db.session.add(new_artist)
        
        # Fetch and save tracks and genres
        tracks = fetch_top_tracks_for_artist_with_genres(artist["artist_name"], limit=20)
        for track in tracks:
            existing_song = Song.query.filter_by(song_id=track["song_id"]).first()
            if not existing_song:
                new_song = Song(
                    song_id=track["song_id"],
                    title=track["title"],
                    genre=None  # Set genre later or as needed
                )
                db.session.add(new_song)
            
            # Associate songs with artists
            song_artist = SongArtist.query.filter_by(song_id=track["song_id"], artist_id=artist["artist_id"]).first()
            if not song_artist:
                new_song_artist = SongArtist(
                    song_id=track["song_id"],
                    artist_id=artist["artist_id"]
                )
                db.session.add(new_song_artist)

    db.session.commit()
    print("Database population completed!")
