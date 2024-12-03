document.addEventListener("DOMContentLoaded", () => {
    const mainSearchInput = document.getElementById("mainSongSearch");
    const mainDropdown = document.getElementById("mainSongDropdown");

    mainSearchInput.addEventListener("input", () => {
        searchSongs(mainSearchInput.value, (songs) => {
            populateSongList(mainDropdown, songs);
        });
    });
});

function searchSongs(query, callback) {
    if (!query) {
        callback([]);
        return;
    }

    fetch(`/search_song?query=${encodeURIComponent(query)}`)
        .then((response) => response.json())
        .then((songs) => callback(songs))
        .catch((error) => console.error("Error fetching songs:", error));
}

function populateSongList(listElement, songs) {
    listElement.innerHTML = ""; // Clear existing options

    if (songs.length === 0) {
        const listItem = document.createElement("li");
        listItem.className = "list-group-item";
        listItem.textContent = "No songs found";
        listItem.disabled = true;
        listElement.appendChild(listItem);
    } else {
        songs.forEach((song) => {
            const listItem = document.createElement("li");
            listItem.className = "list-group-item d-flex justify-content-between align-items-center";

            const title = document.createElement("span");
            title.textContent = song.title;

            const addButton = document.createElement("button");
            addButton.className = "btn btn-primary btn-sm";
            addButton.textContent = "+";
            addButton.onclick = () => handleAddSong(song.song_id);

            listItem.appendChild(title);
            listItem.appendChild(addButton);
            listElement.appendChild(listItem);
        });
    }
}

function handleAddSong(songId) {
    fetch(`/get_playlists`)
        .then((response) => response.json())
        .then((data) => {
            if (data.playlists.length === 0) {
                alert("No playlists found. Please create a playlist first.");
            } else if (data.playlists.length === 1) {
                submitAddToPlaylist(songId, data.playlists[0].id);
            } else {
                displayPlaylistSelectionModal(songId, data.playlists);
            }
        })
        .catch((error) => console.error("Error fetching playlists:", error));
}

function displayPlaylistSelectionModal(songId, playlists) {
    const playlistOptions = playlists
        .map((playlist) => `<option value="${playlist.id}">${playlist.name}</option>`)
        .join("");

    const modal = `
        <div class="modal" id="playlistSelectionModal">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Select Playlist</h5>
                        <button type="button" class="close" onclick="closeModal()" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <select id="playlistSelect" class="form-control">
                            ${playlistOptions}
                        </select>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="submitAddToPlaylist(${songId})">Add</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML("beforeend", modal);
    document.getElementById("playlistSelectionModal").style.display = "block";
}

function closeModal() {
    const modal = document.getElementById("playlistSelectionModal");
    if (modal) {
        modal.remove();
    }
}

function submitAddToPlaylist(songId, playlistId) {
    playlistId = playlistId || document.getElementById("playlistSelect").value;

    fetch(`/add_song_to_playlist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ song_id: songId, playlist_id: playlistId }),
    })
        .then((response) => {
            if (response.ok) {
                alert("Song added to playlist successfully!");
                closeModal();
            } else {
                alert("Failed to add song to playlist.");
            }
        })
        .catch((error) => console.error("Error adding song to playlist:", error));
}
