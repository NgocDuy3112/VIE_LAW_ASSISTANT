document.addEventListener('DOMContentLoaded', () => {
    const uploadBtn = document.getElementById('uploadBtn');
    const pdfInput = document.getElementById('pdfInput');
    const pdfIframe = document.getElementById('pdfIframe');
    const placeholderText = document.getElementById('placeholderText');
    const sendBtn = document.getElementById('sendBtn');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');

    // Trigger file input when '+' icon is clicked
    uploadBtn.addEventListener('click', () => {
        pdfInput.click();
    });

    // Handle PDF upload and display
    pdfInput.addEventListener('change', function () {
        const file = this.files[0];
        if (file && file.type === 'application/pdf') {
            const fileURL = URL.createObjectURL(file);
            pdfIframe.src = fileURL;
            pdfIframe.hidden = false;
            if (placeholderText) placeholderText.style.display = 'none';
        }
    });

    // Function to send chat message
    async function sendChatMessage() {
        const text = chatInput.value.trim();
        if (text) {
            // Display user message
            const msg = document.createElement('div');
            msg.className = 'chat-message user';
            msg.textContent = text;
            chatMessages.appendChild(msg);
            chatInput.value = '';
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // Prepare message payload for LLM API
            const payload = [
                {
                    role: 'user',
                    content: [{ type: 'text', text: text }]
                }
            ];

            // Show loading indicator (optional)
            const loadingMsg = document.createElement('div');
            loadingMsg.className = 'chat-message ai';
            loadingMsg.textContent = '...';
            chatMessages.appendChild(loadingMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            try {
                const response = await fetch('http://localhost:8001/v1/chat/completions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                if (!response.ok) {
                    throw new Error('API error');
                }
                const data = await response.json();
                // Remove loading indicator
                chatMessages.removeChild(loadingMsg);
                // Display AI message
                const aiMsg = document.createElement('div');
                aiMsg.className = 'chat-message ai';
                // If content is an array of dicts, join text fields
                if (Array.isArray(data.content)) {
                    aiMsg.textContent = data.content.map(c => c.text || '').join(' ');
                } else {
                    aiMsg.textContent = data.content || '';
                }
                chatMessages.appendChild(aiMsg);
            } catch (err) {
                // Remove loading indicator
                chatMessages.removeChild(loadingMsg);
                const errorMsg = document.createElement('div');
                errorMsg.className = 'chat-message ai';
                errorMsg.textContent = 'Error: Could not get response from AI.';
                chatMessages.appendChild(errorMsg);
            }
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    sendBtn.addEventListener('click', sendChatMessage);

    // Send chat on Enter key
    chatInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendChatMessage();
        }
    });
});