let chatSocket = null;

function chat(url)
{
	console.log("hace chatsocket");
    //const chatSocket = new WebSocket('ws://' + window.location.host + '/ws/ws/chat/');
	
    const accessToken = sessionStorage.getItem('access');
    if (!accessToken) {
        console.error('No se encontró el token de acceso en sessionStorage. No se puede conectar al chat.');
        // window.location.href = '/users/login/';
        // TODO: Redirigir al login o mostrar un mensaje ?
        return; 
    }
	
    console.log(`url de donde extraer id: <${url}>`);
	const params = new URLSearchParams(new URL(url).search);
    const otherUserId = params.get("user"); // Asumo que 'user' es el ID del otro usuario
   
    const hostname = window.location.hostname;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        hostname += ':8080';
    }
    const route = `${protocol}//${hostname}/ws/chat/${otherUserId}/?token=${accessToken}`;
    
    chatSocket = new WebSocket(route); 
    console.log("Intentando conectar a:", route); 
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