function fetchArtists(query, suggestionListId) {
    const suggestionList = document.getElementById(suggestionListId);
    suggestionList.innerHTML = ''; // Clear previous suggestions

    if (!query.trim()) return; // Exit if query is empty

    fetch(`/search_artists?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                const noResultsItem = document.createElement('li');
                noResultsItem.textContent = 'No artists found';
                suggestionList.appendChild(noResultsItem);
            } else {
                data.forEach(artist => {
                    const listItem = document.createElement('li');
                    listItem.textContent = artist.name;
                    listItem.addEventListener('click', () => {
                        document.querySelector(`#${suggestionListId}`).previousElementSibling.value = artist.name;
                        suggestionList.innerHTML = ''; // Clear suggestions
                    });
                    suggestionList.appendChild(listItem);
                });
            }
        })
        .catch(error => console.error('Error fetching artists:', error));
}
