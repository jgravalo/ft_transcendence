function Match()
{
    const ruta = "ws://" + window.location.host + "/game/sock"; // wss:// si usamos https
    console.log(ruta);
    const socket = new WebSocket(ruta);

        // Evento cuando la conexión se abre
        socket.onopen = function(e) {
            console.log("Conexión establecida");
        };

        // Evento cuando se recibe un mensaje
        socket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            console.log("Mensaje recibido:", data.message);
        };

        // Evento cuando la conexión se cierra
        socket.onclose = function(e) {
            console.log("Conexión cerrada");
        };

        // Evento cuando hay un error
        socket.onerror = function(e) {
            console.error("Error en el WebSocket", e);
        };

        // Enviar un mensaje al WebSocket
        document.getElementById('sendMessageButton').onclick = function() {
            socket.send(JSON.stringify({
                'message': 'Hola desde el cliente!'
            }));
        };
}