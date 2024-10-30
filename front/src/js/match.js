function Match()
{
/*  var n1 = 0;
    var n2 = 0;

    document.getElementById('n1').textContent = n1;
    document.getElementById('n2').textContent = n2; */
   
    //const ruta = "ws://" + window.location.host + "/ws/game/sock"; // wss:// si usamos https
    const ruta = "ws://localhost:8000/ws/game/sock"; // wss:// si usamos https
    console.log(ruta);
    const socket = new WebSocket(ruta);

    socket.onopen = function(event) {
        console.log("Conexión WebSocket abierta");
    };
    
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log("Mensaje recibido del servidor:", data.message);
    };
    
    socket.onerror = function(event) {
        console.error("Error en WebSocket:", event);
    };
    
    socket.onclose = function(event) {
        console.log("WebSocket cerrado:", event);
    };
    /* 
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
        }; */
}