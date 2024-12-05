$(document).ready(function() {
    // Show the chat window
    $('#chatButton').click(function() {
        $('#chatContainer').toggle();
    });

    // Close the chat window
    $('#closeChat').click(function() {
        $('#chatContainer').hide();
    });

    // Send message
    $('#sendMessage').click(function() {
        const message = $('#userMessage').val();
        if (message.trim() !== "") {
            // Add user message to chat
            $('#chatMessages').append(`<div class="user-message">${message}</div>`);

            // Clear the input field
            $('#userMessage').val("");

            // Send message to backend (OpenAI API integration)
            $.ajax({
                url: '/ask_chatbot',  // Flask endpoint
                method: 'POST',
                data: { message: message },
                success: function(response) {
                    // Display chatbot response
                    $('#chatMessages').append(`<div class="bot-message">${response.answer}</div>`);
                    $('#chatMessages').scrollTop($('#chatMessages')[0].scrollHeight);  // Scroll to the bottom
                }
            });
        }
    });
});
