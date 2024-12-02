from app import app, db
from  app.models import Artist, Song, SongArtist
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

def fetch_top_tracks_for_artist(artist_name, limit=20):
    """
    Fetch the top tracks for a specific artist from Last.fm.
    """
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
        # Safely handle missing fields
        return [
            {
                # Use a safe fallback for missing 'mbid' and 'name'
                "song_id": track.get("mbid") or f"{artist_name.replace(' ', '_').lower()}_{track.get('name', 'unknown').replace(' ', '_').lower()}",
                "title": track.get("name", "Unknown Title")
            }
            for track in tracks if track.get("name")  # Only include tracks with a 'name'
        ]
    else:
        print(f"Error fetching tracks for {artist_name}: {response.status_code} - {response.text}")
        return []


def save_artist_and_songs_to_db(artist_data, song_data):
    """
    Save artist and their songs to the database.
    """
    artist = Artist.query.get(artist_data["artist_id"])
    if not artist:
        artist = Artist(
            artist_id=artist_data["artist_id"],
            artist_name=artist_data["artist_name"],
            listeners=artist_data["listeners"]
        )
        db.session.add(artist)

    for song in song_data:
        existing_song = Song.query.get(song["song_id"])
        if not existing_song:
            new_song = Song(
                song_id=song["song_id"],
                title=song["title"]
            )
            db.session.add(new_song)

            link = SongArtist(
                song_id=song["song_id"],
                artist_id=artist_data["artist_id"]
            )
            db.session.add(link)

    db.session.commit()

def populate_database():
    """
    Main function to populate the database with top artists and their songs.
    """
    top_artists = fetch_top_artists(limit=50)
    for artist in top_artists:
        print(f"Fetching songs for artist: {artist['artist_name']}...")
        top_tracks = fetch_top_tracks_for_artist(artist_name=artist["artist_name"], limit=20)
        save_artist_and_songs_to_db(artist, top_tracks)

    print("Database populated successfully.")
