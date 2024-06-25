function toggleChatbot() {
    var chatbotContainer = document.getElementById('chatbot-container');
    if (chatbotContainer.style.display === 'none' || chatbotContainer.style.display === '') {
        chatbotContainer.style.display = 'flex';
    } else {
        chatbotContainer.style.display = 'none';
    }
}

function handleKeyDown(event) {
    if (event.key === 'Enter') {
        var input = document.getElementById('chatbot-input');
        var message = input.value.trim();
        if (message !== '') {
            addMessage('user', message);
            input.value = '';
            sendToChatbot(message);
        }
    }
}

function addMessage(sender, message) {
    var messagesContainer = document.getElementById('chatbot-messages');
    var messageElement = document.createElement('div');
    messageElement.className = sender + '-message';
    messageElement.textContent = message;
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function sendToChatbot(message) {
    fetch('/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        addMessage('bot', data.reply);
        saveChatLog({ user: message, bot: data.reply });
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function saveChatLog(chatLog) {
    fetch('/save-chat-log', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(chatLog)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Chat log saved:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
