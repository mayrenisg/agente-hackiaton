function sendMessage() {
    var userInput = document.getElementById("user-input");
    var message = userInput.value;

    if (message.trim() === "") return;

    var chatBox = document.getElementById("chat-box");
    var userMessageDiv = document.createElement("div");

    userMessageDiv.className = "message user-message";
    userMessageDiv.textContent = message;

    chatBox.appendChild(userMessageDiv);

    userInput.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    fetch("/chatbot", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            prompt: message
        }),
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error("Error HTTP: " + response.status);
        }

        return response.text();
    })
    .then((data) => {
    var botMessageDiv = document.createElement("div");

    botMessageDiv.className = "message bot-message";
    botMessageDiv.innerHTML = marked.parse(data);

    chatBox.appendChild(botMessageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch((error) => {
        console.error("Error:", error);
    });
}