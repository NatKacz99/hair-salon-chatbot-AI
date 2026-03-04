document.addEventListener("DOMContentLoaded", function() {
    startChatbot()
})

function startChatbot() {
    const chatInput = document.getElementById('chat-input');
    updateSendButtonState();

    const chatToggle = document.getElementById('chat-toggle');
    const chatWidget = document.getElementById('chat-widget');
    const chatClose = document.getElementById('chat-close');
    const chatMessages = document.getElementById('chat-messages');
    const chatFrom = document.getElementById('chat-form');

    chatToggle.addEventListener('click', function() {
        openChat();
    })

    chatClose.addEventListener('click', function() {
        closeChat()
    })

    chatInput.addEventListener('input', updateSendButtonState);

    chatFrom.addEventListener('submit', async function(e) {
        e.preventDefault();

        const messageText = chatInput.value.trim();
        if (!messageText) return;

        addUserMessage(messageText);
        chatInput.value = "";
        showTyping();

        try {
            const response = await fetch("http://127.0.0.1:8000/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: messageText,
                    history: []
                })
            });
            const data = await response.json();

            hideTyping();
            addBotMessageText(data.response);
        } catch (error) {
            addBotMessageText("Błąd połączenia z serwerem.")
            console.error(error);
        }
    })

    function openChat() {
        chatWidget.classList.add('open');
        chatToggle.classList.add('hidden');
    }

    function addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = "message user-message";

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        scrollDown();
    }

    function addBotMessageText(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;

        messageDiv.appendChild(contentDiv);

        chatMessages.appendChild(messageDiv);

        scrollDown();
    }

    function showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'message assistant-message';

        const dotsDiv = document.createElement('div');
        dotsDiv.className = "typing-indicator";
        dotsDiv.innerHTML = '<span></span><span></span><span></span>';

        typingDiv.appendChild(dotsDiv);
        chatMessages.appendChild(typingDiv);

        scrollDown()
    }

    function hideTyping() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    function updateSendButtonState() {
        const sendingButton = document.querySelector('.chat-send-btn');
        sendingButton.disabled = chatInput.value.trim() === "";
    }

    function scrollDown() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function closeChat() {
        chatWidget.classList.remove('open');
        chatToggle.classList.remove('hidden')
    }

}