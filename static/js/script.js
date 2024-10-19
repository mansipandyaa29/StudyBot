// Function to handle the bot response and user input
function getBotResponse() {
    // Get the user's input from the text input field
    var rawText = $("#textInput").val().trim(); // Trim spaces to avoid empty inputs

    // Prevent empty messages from being sent
    if (rawText === "") {
        return;
    }

    // Create HTML for the user's message and append it to the chatbox
    var userHtml = '<p class="userText"><span>' + rawText + "</span></p>";
    // Clear the input field after the user sends a message
    $("#textInput").val("");
    // Append the user's message to the chatbox
    $("#chatbox").append(userHtml);

    // Smooth scroll to the bottom after the user's input
    $("#chatbox").scrollTop($("#chatbox")[0].scrollHeight);

    // Send a GET request to the server, passing the user's message as a query parameter (`msg`)
    $.get("/get", { msg: rawText }).done(function (data) {
        // Create HTML for the bot's response and append it to the chatbox
        var botHtml = '<p class="botText"><span>' + data + "</span></p>";
        $("#chatbox").append(botHtml);

        // Smooth scroll to keep the latest bot response in view
        $("#chatbox").scrollTop($("#chatbox")[0].scrollHeight);
    });
}

// Call getBotResponse() when Enter (key code 13) is pressed
$("#textInput").keypress(function (e) {
    if (e.which == 13) {
        getBotResponse();
    }
});

// function getBotResponse() {
//     // Get the user's input from the text input field
//     var rawText = $("#textInput").val();

//     // Create HTML for the user's message and append it to the chatbox
//     var userHtml = '<p class="userText"><span>' + rawText + "</span></p>";
//     // Clear the input field after the user sends a message
//     $("#textInput").val("");
//     // Append the user's message to the chatbox
//     $("#chatbox").append(userHtml);
//     // Smooth scroll to the user's input area for better UX
//     document.getElementById("userInput").scrollIntoView({ block: "start", behavior: "smooth" });

//     // Send a GET request to the server, passing the user's message as a query parameter (`msg`)
//     $.get("/get", { msg: rawText }).done(function (data) {
//         // Create HTML for the bot's response and append it to the chatbox
//         var botHtml = '<p class="botText"><span>' + data + "</span></p>";
//         $("#chatbox").append(botHtml);
//         // Smooth scroll to keep the user input area in view after bot's response
//         document.getElementById("userInput").scrollIntoView({ block: "start", behavior: "smooth" });
//     });

// }

// // Call getBotResponse() when Enter (key code 13) is pressed
// $("#textInput").keypress(function (e) {
//     if (e.which == 13) {
//         getBotResponse();
//     }
// });