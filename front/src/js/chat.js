
function chat()
{
    console.log("hace chatsocket");
    //const chatSocket = new WebSocket('ws://' + window.location.host + '/ws/ws/chat/');
    const chatSocket = new WebSocket('ws://localhost:8000/ws/chat/?' + 'admin');
    console.log("hizo chatsocket");

    chatSocket.onopen = function () {
        console.log("✅ Conectado al WebSocket");
    };

    chatSocket.onmessage = function(e) {
        console.log("mensaje recibido");
        const data = JSON.parse(e.data);
        const chatLog = document.getElementById('chat-log');
        chatLog.value += data.username + ': ' + data.message + '\n';
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