function sendMessage() {
    var userInput = document.getElementById("user-input");
    var message = userInput.value;

    if (message.trim() === "") return;

    // Display user message
    var chatBox = document.getElementById("chat-box");
    var userMessageDiv = document.createElement("div");

    userMessageDiv.className = "message user-message";
    userMessageDiv.textContent = message;

    chatBox.appendChild(userMessageDiv);

    // Clear input
    userInput.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // Send message to chatbot backend
    fetch("/chatbot", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            prompt: message
        }),
    })
    .then((response) => response.text())
    .then((data) => {
    var botMessageDiv = document.createElement("div");

    botMessageDiv.className = "message bot-message";
    botMessageDiv.textContent = data;

    chatBox.appendChild(botMessageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch((error) => {
        console.error("Error:", error);
    });
}