document.addEventListener("DOMContentLoaded", () => {
    const mainArtistSearchInput = document.getElementById("mainArtistSearch");
    const mainArtistDropdown = document.getElementById("mainArtistDropdown");

    mainArtistSearchInput.addEventListener("input", () => {
        searchArtists(mainArtistSearchInput.value, (artists) => {
            populateArtistList(mainArtistDropdown, artists);
        });
    });
});

function searchArtists(query, callback) {
    if (!query) {
        callback([]);
        return;
    }

    fetch(`/search_artist?query=${encodeURIComponent(query)}`)
        .then((response) => response.json())
        .then((artists) => callback(artists))
        .catch((error) => console.error("Error fetching artists:", error));
}

function populateArtistList(listElement, artists) {
    listElement.innerHTML = ""; // Clear existing options

    if (artists.length === 0) {
        const listItem = document.createElement("li");
        listItem.className = "list-group-item";
        listItem.textContent = "No artists found";
        listItem.disabled = true;
        listElement.appendChild(listItem);
    } else {
        artists.forEach((artist) => {
            const listItem = document.createElement("li");
            listItem.className = "list-group-item d-flex justify-content-between align-items-center";

            const title = document.createElement("span");
            title.textContent = artist.name;

            const viewButton = document.createElement("button");
            viewButton.className = "btn btn-primary btn-sm";
            viewButton.textContent = "View Songs";
            viewButton.onclick = () => window.location.href = `/artist_songs/${artist.id}`; // Redirect to artist's songs page

            listItem.appendChild(title);
            listItem.appendChild(viewButton);
            listElement.appendChild(listItem);
        });
    }
}
