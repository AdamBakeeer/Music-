document.addEventListener("DOMContentLoaded", () => {
    // Main Page Search
    const mainSearchInput = document.getElementById("mainSongSearch");
    const mainDropdown = document.getElementById("mainSongDropdown");

    mainSearchInput.addEventListener("input", () => {
        const query = mainSearchInput.value.trim();
        if (!query) {
            mainDropdown.innerHTML = "<li class='list-group-item'>Type to search for songs...</li>";
            return;
        }

        fetch(`/search_song?query=${encodeURIComponent(query)}`)
            .then((response) => response.json())
            .then((songs) => populateSongList(mainDropdown, songs))
            .catch((error) => console.error("Error fetching songs:", error));
    });

    // Add Playlist Modal Song Search
    const modalSearchInput = document.getElementById("songSearch");
    const modalDropdown = document.getElementById("songDropdown");

    modalSearchInput.addEventListener("input", () => {
        const query = modalSearchInput.value.trim();
        if (!query) {
            modalDropdown.innerHTML = "<option>No songs found</option>";
            return;
        }

        fetch(`/search_song?query=${encodeURIComponent(query)}`)
            .then((response) => response.json())
            .then((songs) => populateSongDropdown(modalDropdown, songs))
            .catch((error) => console.error("Error fetching songs:", error));
    });

    function populateSongList(listElement, songs) {
        listElement.innerHTML = ""; // Clear previous results

        if (songs.length === 0) {
            const noResultsItem = document.createElement("li");
            noResultsItem.className = "list-group-item";
            noResultsItem.textContent = "No songs found.";
            listElement.appendChild(noResultsItem);
            return;
        }

        songs.forEach((song) => {
            const listItem = document.createElement("li");
            listItem.className = "list-group-item d-flex justify-content-between align-items-center";

            const title = document.createElement("span");
            title.textContent = song.title;

            const addButton = document.createElement("button");
            addButton.className = "btn btn-primary btn-sm";
            addButton.textContent = "+";
            addButton.onclick = () => addSongToPlaylist(song.song_id);

            listItem.appendChild(title);
            listItem.appendChild(addButton);
            listElement.appendChild(listItem);
        });
    }

    function populateSongDropdown(dropdown, songs) {
        dropdown.innerHTML = ""; // Clear existing options

        if (songs.length === 0) {
            const noResultsOption = document.createElement("option");
            noResultsOption.textContent = "No songs found.";
            noResultsOption.disabled = true;
            dropdown.appendChild(noResultsOption);
            return;
        }

        songs.forEach((song) => {
            const option = document.createElement("option");
            option.value = song.song_id;
            option.textContent = song.title;
            dropdown.appendChild(option);
        });
    }

    // Function to add a song to the playlist (both main page and modal)
    function addSongToPlaylist(songId) {
        // Assuming you have a playlist selected or create a new playlist logic
        const playlistId = getCurrentPlaylistId(); // You can implement this function to get the current playlist ID

        fetch(`/add_song_to_playlist`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                song_id: songId,
                playlist_id: playlistId,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Song added to the playlist!");
                // Optionally, update the UI (e.g., disable the add button or refresh the playlist)
            } else {
                alert("Failed to add song to the playlist.");
            }
        })
        .catch(error => console.error("Error adding song to playlist:", error));
    }

    function getCurrentPlaylistId() {
        // This function should return the current playlist ID, or handle the logic for playlist selection
        // Example: return document.getElementById("playlistSelect").value;
        return 1;  // Placeholder for playlist ID
    }
});
