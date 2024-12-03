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
            addButton.onclick = () => alert(`Add ${song.title} to a playlist!`);

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
});
