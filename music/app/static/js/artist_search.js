document.addEventListener("DOMContentLoaded", () => {
    const mainSearchInput = document.getElementById("mainArtistSearch");
    const artistResults = document.getElementById("artistResults");

    // Handle artist search input
    mainSearchInput.addEventListener("input", () => {
        searchArtists(mainSearchInput.value, (artists) => {
            populateArtistResults(artistResults, artists);
        });
    });

    // Search for artists (AJAX)
    function searchArtists(query, callback) {
        if (!query) {
            callback([]);  // Return empty array if no query is provided
            return;
        }

        fetch(`/search_artist?query=${encodeURIComponent(query)}`)
            .then((response) => response.json())
            .then((artists) => callback(artists))
            .catch((error) => console.error("Error fetching artists:", error));
    }

    // Populate artist results dynamically
    function populateArtistResults(container, artists) {
        container.innerHTML = "";  // Clear existing content

        if (artists.length === 0) {
            const noResults = document.createElement("div");
            noResults.className = "col-12 text-center";
            noResults.textContent = "No artists found.";
            container.appendChild(noResults);
        } else {
            artists.forEach((artist) => {
                const artistCard = document.createElement("div");
                artistCard.className = "col-12 col-sm-6 col-md-4 mb-4";  // Responsive grid for 3 cards per row

                artistCard.innerHTML = `
                    <div class="card h-100 shadow-lg" style="border: 2px solid #6a0dad; background-color: #f9f9f9;">
                        <div class="card-body d-flex flex-column justify-content-between">
                            <h5 class="card-title text-dark">${artist.artist_name}</h5>
                            <a href="/view_artist_songs/${artist.artist_id}" class="btn btn-purple mt-3" 
                               style="background-color: #6a0dad; color: white; border-color: #6a0dad;">View Songs</a>
                        </div>
                    </div>
                `;
                container.appendChild(artistCard);
            });
        }
    }
});
