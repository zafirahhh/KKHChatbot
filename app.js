document.addEventListener("DOMContentLoaded", () => {
    const chatWindow = document.getElementById("chat-window");
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const newChatBtn = document.getElementById("new-chat-btn");
    const clearChatBtn = document.getElementById("clear-chat-btn");

    chatForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const userMessage = userInput.value.trim();
        if (!userMessage) return;

        // Add user message to chat window
        const userBubble = document.createElement("div");
        userBubble.className = "message user";
        userBubble.innerHTML = `<span class='avatar'>👩</span><span class='bubble'>${userMessage}</span>`;
        chatWindow.appendChild(userBubble);

        // Clear input field
        userInput.value = "";

        // Add typing indicator
        const typingIndicator = document.createElement("div");
        typingIndicator.className = "message bot";
        typingIndicator.innerHTML = `<span class='avatar'>🤖</span><span class='bubble'>Typing...</span>`;
        chatWindow.appendChild(typingIndicator);

        // Scroll to the bottom
        chatWindow.scrollTop = chatWindow.scrollHeight;

        try {
            // Send message to backend
            const response = await fetch("/ask", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ question: userMessage }),
            });

            if (!response.ok) {
                throw new Error("Failed to fetch response from server");
            }

            const data = await response.json();

            // Remove typing indicator
            chatWindow.removeChild(typingIndicator);

            // Add bot response to chat window
            const botBubble = document.createElement("div");
            botBubble.className = "message bot";
            botBubble.innerHTML = `<span class='avatar'>🤖</span><span class='bubble'>${data}</span>`;
            chatWindow.appendChild(botBubble);

            // Scroll to the bottom
            chatWindow.scrollTop = chatWindow.scrollHeight;
        } catch (error) {
            console.error("Error:", error);

            // Remove typing indicator
            chatWindow.removeChild(typingIndicator);

            // Add error message to chat window
            const errorBubble = document.createElement("div");
            errorBubble.className = "message bot";
            errorBubble.innerHTML = `<span class='avatar'>🤖</span><span class='bubble'>Sorry, something went wrong. Please try again later.</span>`;
            chatWindow.appendChild(errorBubble);

            // Scroll to the bottom
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
    });

    newChatBtn.addEventListener("click", () => {
        chatWindow.innerHTML = "";
    });

    clearChatBtn.addEventListener("click", () => {
        chatWindow.innerHTML = "";
        localStorage.clear();
    });
});
