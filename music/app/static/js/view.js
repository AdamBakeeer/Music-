document.addEventListener("DOMContentLoaded", () => {
    // Select all remove buttons
    const removeButtons = document.querySelectorAll(".remove-song-btn");

    removeButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const songId = button.dataset.songId;
            const playlistId = button.dataset.playlistId;

            // Confirm the action before sending request
            const confirmRemoval = confirm("Are you sure you want to remove this song from the playlist?");
            if (!confirmRemoval) return;

            // Send the song and playlist IDs to the server
            fetch("/remove_song", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector("input[name='_csrf_token']").value // CSRF token
                },
                body: JSON.stringify({
                    song_id: songId,
                    playlist_id: playlistId
                }),
            })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    // Remove the song's card from the DOM
                    button.closest(".col-md-4").remove();
                    alert("Song removed successfully!");
                } else {
                    alert(`Error: ${data.message}`);
                }
            })
            .catch((error) => {
                console.error("An error occurred while removing the song:", error);
                alert("An error occurred while removing the song.");
            });
        });
    });
});
