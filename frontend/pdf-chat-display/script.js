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

    // Send chat message (user)
    sendBtn.addEventListener('click', () => {
        const text = chatInput.value.trim();
        if (text) {
            const msg = document.createElement('div');
            msg.className = 'chat-message user';
            msg.textContent = text;
            chatMessages.appendChild(msg);
            chatInput.value = '';

            // Example: Simulate AI response (for demo)
            setTimeout(() => {
                const aiMsg = document.createElement('div');
                aiMsg.className = 'chat-message ai';
                aiMsg.textContent = 'This is an AI response.';
                chatMessages.appendChild(aiMsg);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }, 600);
        }
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
});