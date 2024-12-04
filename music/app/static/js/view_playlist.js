document.addEventListener("DOMContentLoaded", () => {
    // Function to remove a song from the playlist
    function removeSongFromPlaylist(songId, playlistId) {
        if (confirm('Are you sure you want to remove this song from the playlist?')) {
            fetch(`/remove_song_from_playlist`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ song_id: songId, playlist_id: playlistId }),
            })
            .then(response => {
                if (response.ok) {
                    location.reload(); // Reload the page to update the song list
                } else {
                    alert('Failed to remove song from playlist');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    }

    // Attach remove functionality to all buttons after the page loads
    const removeButtons = document.querySelectorAll('.remove-song-btn');
    removeButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const songId = e.target.getAttribute('data-song-id');
            const playlistId = e.target.getAttribute('data-playlist-id');
            removeSongFromPlaylist(songId, playlistId);
        });
    });
});
