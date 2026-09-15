document.addEventListener('DOMContentLoaded', () => {
    const openBtn = document.getElementById('open-chat-btn');
    const closeBtn = document.getElementById('close-chat-btn');
    const chatModal = document.getElementById('chat-modal');
    const sendBtn = document.getElementById('chat-send-btn');
    const inputField = document.getElementById('chat-user-input');
    const chatMessages = document.getElementById('chat-messages');

    if (openBtn && chatModal) {
        openBtn.addEventListener('click', () => {
            chatModal.classList.remove('hidden');
            inputField.focus();
        });
    }

    if (closeBtn && chatModal) {
        closeBtn.addEventListener('click', () => {
            chatModal.classList.add('hidden');
        });
    }

    function appendMessage(text, role) {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${role}`;
        bubble.textContent = text;
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function handleSend() {
        const text = inputField.value.trim();
        if (!text) return;

        appendMessage(text, 'user');
        inputField.value = '';

        const tempBotMsg = document.createElement('div');
        tempBotMsg.className = 'chat-bubble bot';
        tempBotMsg.textContent = '호치가 불닭 레시피 사전 뒤지는 중... 꼬꼬!';
        chatMessages.appendChild(tempBotMsg);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();
            tempBotMsg.textContent = data.reply || '오류가 발생했습니다.';
        } catch (err) {
            tempBotMsg.textContent = '네트워크 연결 상태가 화끈하지 못합니다 주인님!';
        }
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', handleSend);
    }
    if (inputField) {
        inputField.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') handleSend();
        });
    }
});
