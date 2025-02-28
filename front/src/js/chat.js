let chatSocket = null;

function chat(url)
{
    const params = new URLSearchParams(new URL(url).search);
    console.log("hace chatsocket");
    //const chatSocket = new WebSocket('ws://' + window.location.host + '/ws/ws/chat/');
    chatSocket = new WebSocket('ws://' + base.slice(7, -5) + ':8080/ws/chat/' + params.get("user") + '/');
    console.log("hizo chatsocket");

    chatSocket.onopen = function () {
        console.log("✅ Conectado al WebSocket");
    };

    chatSocket.onmessage = function(e) {
        console.log("mensaje recibido");
        const data = JSON.parse(e.data);
        /* const chatLog = document.getElementById('chat-log');
        chatLog.value += data.sender + ': ' + data.message + '\n'; */

        let chatBox = document.getElementById("chat-box");
        let messageDiv = document.createElement("div");
        // messageDiv.classList.add("message", sender);
        console.log("sender:", data.sender);
        console.log("message:", data.message);
        messageDiv.innerText = data.message;
        messageDiv.classList.add("message");
        if (data.role) {
            messageDiv.classList.add(data.role);
        }
        console.log("messageDiv:", messageDiv);
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        messageDiv.offsetHeight; // Esto obliga al navegador a "redibujar"
    };

    chatSocket.onclose = function(e) {
        console.error('Chat cerrado.');
    };

    chatSocket.onerror = function(e) {
        console.error('Fallo chatsocket.');
    };

    document.getElementById("message-bar").addEventListener("submit", function(event) {
        event.preventDefault();  // Evita que el formulario redirija la página

        console.log("escribe en socket");
        const messageInput = document.getElementById("message-input");
        const message = messageInput.value;
    
        if (message.trim() !== "") {
            chatSocket.send(JSON.stringify({
                // 'username': username,
                message: message
            }));  // 🔹 Envía mensaje por WebSocket
            messageInput.value = "";  // 🔹 Limpia el input
        }
    });

    /* function sendMessage() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value;

        chatSocket.send(JSON.stringify({
            'username': username,
            'message': message
        }));

        messageInput.value = '';
    } */
}