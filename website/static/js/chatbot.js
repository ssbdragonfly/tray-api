function toggleChatbot() {
    var chatbotContainer = document.getElementById('chatbot-container');
    var chatbotButton = document.getElementById('chatbot-button');
    
    if (chatbotContainer.style.display === 'none' || chatbotContainer.style.display === '') {
        chatbotContainer.style.display = 'flex';
        chatbotButton.style.opacity = '0';
        chatbotButton.style.pointerEvents = 'none';
    } else {
        chatbotContainer.style.display = 'none';
        chatbotButton.style.opacity = '1';
        chatbotButton.style.pointerEvents = 'auto';
    }
}

function handleKeyDown(event) {
    if (event.key === 'Enter') {
        var input = document.getElementById('chatbot-input-field');
        var message = input.value.trim();
        if (message !== '') {
            sendToChatbot(message);
            input.value = '';
        }
    }
}

function addMessage(sender, message) {
    var messagesContainer = document.getElementById('chatbot-messages');
    var messageElement = document.createElement('div');
    messageElement.className = sender + '-message message';
    messageElement.innerHTML = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function sendToChatbot(message) {
    addMessage('user', message);
    showLoadingIndicator();
    fetch('/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingIndicator();
        addMessage('bot', data.reply);
        saveChatLog({ user: message, bot: data.reply });
    })
    .catch(error => {
        hideLoadingIndicator();
        console.error('Error:', error);
        addMessage('bot', 'Sorry, there was an error processing your request.');
    });
}

function showLoadingIndicator() {
    const loadingIndicator = document.createElement('div');
    loadingIndicator.id = 'chatbot-loading';
    loadingIndicator.textContent = 'Thinking...';
    document.getElementById('chatbot-messages').appendChild(loadingIndicator);
}

function hideLoadingIndicator() {
    const loadingIndicator = document.getElementById('chatbot-loading');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
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