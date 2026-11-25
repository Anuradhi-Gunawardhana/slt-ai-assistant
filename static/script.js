
const form = document.getElementById("chat-form");
const input = document.getElementById("message");
const chatBox = document.getElementById("chat-box");

const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .content;

function addMessage(text, sender) {
    const message = document.createElement("div");

    message.className = "message " + sender;
    message.textContent = text;

    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;

    return message;
}

form.addEventListener("submit", async function(event) {
    event.preventDefault();

    const question = input.value.trim();

    if (!question) return;

    addMessage(question, "user");

    input.value = "";

    const thinkingMessage = addMessage(
        "Thinking...",
        "bot"
    );

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken
            },
            body: JSON.stringify({
                message: question
            })
        });

        const result = await response.json();

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!response.ok) {
            throw new Error(
                result.error || "Request failed"
            );
        }

        thinkingMessage.textContent = result.answer;

        if (result.sources && result.sources.length > 0) {
            const sourceText = document.createElement("small");

            sourceText.textContent =
                "Sources: " + result.sources.join(", ");

            thinkingMessage.appendChild(sourceText);
        }

    } catch (error) {

        thinkingMessage.textContent =
            "Sorry, something went wrong. Please try again.";

        console.error(error);
    }
});

