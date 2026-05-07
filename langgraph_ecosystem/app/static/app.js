document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('user-input');
    const messagesArea = document.getElementById('messages-area');
    const threadIdDisplay = document.getElementById('thread-id-display');
    
    // Generar un thread_id aleatorio para la sesión
    const sessionId = 'session_' + Math.random().toString(36).substring(2, 9);
    threadIdDisplay.textContent = sessionId;

    // Auto-resize textarea
    input.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if(this.value === '') this.style.height = 'auto';
    });

    // Permitir enviar con Enter (y shift+Enter para nueva línea)
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            form.dispatchEvent(new Event('submit'));
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = input.value.trim();
        if (!message) return;

        // Limpiar input y restablecer altura
        input.value = '';
        input.style.height = 'auto';

        // Añadir mensaje del usuario
        addMessage(message, 'user');

        // Mostrar indicador de "escribiendo..."
        const typingIndicator = addTypingIndicator();

        try {
            // Petición al backend FastAPI
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_input: message,
                    thread_id: sessionId
                })
            });

            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }

            const data = await response.json();
            
            // Eliminar indicador
            typingIndicator.remove();
            
            // Añadir respuesta del asistente
            addMessage(data.response, 'assistant');

        } catch (error) {
            console.error('Error:', error);
            typingIndicator.remove();
            addMessage('Lo siento, ha ocurrido un error al conectar con el servidor.', 'assistant');
        }
    });

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatarText = sender === 'user' ? 'ME' : 'NX';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatarText}</div>
            <div class="message-content">
                <p>${escapeHTML(text).replace(/\n/g, '<br>')}</p>
            </div>
        `;
        
        messagesArea.appendChild(messageDiv);
        scrollToBottom();
    }

    function addTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message assistant typing-message`;
        
        messageDiv.innerHTML = `
            <div class="message-avatar">NX</div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        messagesArea.appendChild(messageDiv);
        scrollToBottom();
        return messageDiv;
    }

    function scrollToBottom() {
        messagesArea.scrollTo({
            top: messagesArea.scrollHeight,
            behavior: 'smooth'
        });
    }

    function escapeHTML(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }
});
