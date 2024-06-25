document.addEventListener('DOMContentLoaded', (event) => {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);

    const toggleButton = document.getElementById('theme-toggle');
    if (theme === 'dark') {
        toggleButton.classList.add('fa-sun');
        toggleButton.classList.remove('fa-moon');
    } else {
        toggleButton.classList.add('fa-moon');
        toggleButton.classList.remove('fa-sun');
    }

    console.log(`Current theme on load: ${theme}`);
});

function toggleTheme() {
    let currentTheme = document.documentElement.getAttribute('data-theme');
    let targetTheme = 'light';

    if (currentTheme === 'light') {
        targetTheme = 'dark';
    }

    document.documentElement.setAttribute('data-theme', targetTheme);
    localStorage.setItem('theme', targetTheme);

    const toggleButton = document.getElementById('theme-toggle');
    if (targetTheme === 'dark') {
        toggleButton.classList.add('fa-sun');
        toggleButton.classList.remove('fa-moon');
    } else {
        toggleButton.classList.add('fa-moon');
        toggleButton.classList.remove('fa-sun');
    }

    console.log(`Theme toggled to: ${targetTheme}`);
}
document.addEventListener('DOMContentLoaded', function () {
    const helpButton = document.getElementById('helpButton');
    const chatbotPopup = document.getElementById('chatbotPopup');
    const closeButton = document.getElementById('closeChatbot');

    helpButton.addEventListener('click', function () {
        chatbotPopup.style.display = 'block';
        helpButton.style.display = 'none';
    });

    closeButton.addEventListener('click', function () {
        chatbotPopup.style.display = 'none';
        helpButton.style.display = 'block';
    });

    const inputField = document.getElementById('chatbotInput');
    inputField.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            document.getElementById('sendMessage').click();
        }
    });

    document.getElementById('sendMessage').addEventListener('click', function () {
        const userMessage = inputField.value;
        if (userMessage.trim() === '') return;

        const chatLog = document.getElementById('chatLog');
        chatLog.innerHTML += `<div class="user-message">${userMessage}</div>`;

        fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userMessage })
        })
        .then(response => response.json())
        .then(data => {
            chatLog.innerHTML += `<div class="bot-reply">${data.reply}</div>`;
            saveChatLog(userMessage, data.reply);
        })
        .catch(error => {
            chatLog.innerHTML += `<div class="bot-reply">Error communicating with the chatbot API.</div>`;
        });

        inputField.value = '';
        chatLog.scrollTop = chatLog.scrollHeight;
    });

    function saveChatLog(userMessage, botReply) {
        fetch('/save-chat-log', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_message: userMessage, bot_reply: botReply })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status !== 'success') {
                console.error('Error saving chat log:', data.message);
            }
        })
        .catch(error => {
            console.error('Error saving chat log:', error);
        });
    }
});
