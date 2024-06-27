let isDragging = false;
let isResizing = false;
let startX, startY, startWidth, startHeight;

function initChatbot() {
    const chatbotContainer = document.getElementById('chatbot-container');
    const chatbotHeader = document.getElementById('chatbot-header');
    const resizeHandle = document.getElementById('chatbot-resize-handle');

    chatbotHeader.addEventListener('mousedown', startDragging);
    resizeHandle.addEventListener('mousedown', startResizing);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDraggingAndResizing);
}

function startDragging(e) {
    isDragging = true;
    startX = e.clientX - chatbotContainer.offsetLeft;
    startY = e.clientY - chatbotContainer.offsetTop;
}

function startResizing(e) {
    isResizing = true;
    startX = e.clientX;
    startY = e.clientY;
    startWidth = parseInt(document.defaultView.getComputedStyle(chatbotContainer).width, 10);
    startHeight = parseInt(document.defaultView.getComputedStyle(chatbotContainer).height, 10);
}

function drag(e) {
    if (isDragging) {
        const newX = e.clientX - startX;
        const newY = e.clientY - startY;
        chatbotContainer.style.left = `${newX}px`;
        chatbotContainer.style.top = `${newY}px`;
    } else if (isResizing) {
        const newWidth = startWidth + (e.clientX - startX);
        const newHeight = startHeight + (e.clientY - startY);
        chatbotContainer.style.width = `${newWidth}px`;
        chatbotContainer.style.height = `${newHeight}px`;
    }
}

function stopDraggingAndResizing() {
    isDragging = false;
    isResizing = false;
}

function toggleChatbot() {
    var chatbotContainer = document.getElementById('chatbot-container');
    var chatbotButton = document.getElementById('chatbot-button');
    
    if (chatbotContainer.style.display === 'none' || chatbotContainer.style.display === '') {
        chatbotContainer.style.display = 'flex';
        chatbotButton.style.display = 'none';
    } else {
        chatbotContainer.style.display = 'none';
        chatbotButton.style.display = 'flex';
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
document.addEventListener('DOMContentLoaded', initChatbot);