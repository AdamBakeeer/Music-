document.addEventListener("DOMContentLoaded", () => {
    const mainSearchInput = document.getElementById("mainSongSearch");
    const songResults = document.getElementById("songResults");

    // Handle song search input
    mainSearchInput.addEventListener("input", () => {
        searchSongs(mainSearchInput.value, (songs) => {
            populateSongResults(songResults, songs);
        });
    });

    // Search for songs (AJAX)
    function searchSongs(query, callback) {
        if (!query) {
            callback([]);
            return;
        }

        fetch(`/search_song?query=${encodeURIComponent(query)}`)
            .then((response) => response.json())
            .then((data) => callback(data.songs)) // Using `data.songs` from the response
            .catch((error) => console.error("Error fetching songs:", error));
    }

    // Populate song results dynamically
    function populateSongResults(container, songs) {
        container.innerHTML = ""; // Clear existing content

        if (songs.length === 0) {
            const noResults = document.createElement("div");
            noResults.className = "col-12 text-center text-muted";
            noResults.textContent = "No songs found.";
            container.appendChild(noResults);
        } else {
            songs.forEach((song) => {
                const songCard = document.createElement("div");
                songCard.className = "col-md-4 mb-4 d-flex justify-content-center";

                // Create a card with title and artist(s)
                songCard.innerHTML = `
                    <div class="card h-100" style="border: 2px solid #6a0dad; background-color: #f9f9f9; color: #6a0dad; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title">${song.title}</h5>
                            <h6 class="card-subtitle mb-2 text-muted">
                                Artist(s): ${song.artists.length > 0 ? song.artists.join(", ") : "Unknown"}
                            </h6>
                        </div>
                    </div>
                `;
                container.appendChild(songCard);
            });
        }
    }
});
