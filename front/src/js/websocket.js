function testWebSocket()
{
    //const ruta = "ws://" + window.location.host + "/ws/game/"; // wss:// si usamos https
    
    const socket = new WebSocket('ws://localhost:8000/ws/game/');
    
    // Escuchar eventos de conexión
    socket.onopen = function (event) {
        console.log("WebSocket conectado");
        socket.send(JSON.stringify({ message: "Hola desde el frontend" }));
    };
    
    // Escuchar mensajes desde el servidor
    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        console.log("Mensaje recibido del servidor:", data.message);
    };
    
    document.addEventListener('keydown', function(event) 
    {
        if ((event.key === 'ArrowUp' || event.key === 'w')
            && top - speed > minY)
        {
            socket.send(JSON.stringify({ message: "flecha arriba" }));
            player.style.marginTop = (top - speed) + 'px';
        }
        else if ((event.key === 'ArrowDown' || event.key === 's')
            && top + speed < maxY - playerHeight - 30)
        {
            socket.send(JSON.stringify({ message: "flecha abajo" }));
            //player.style.marginTop = (top + speed) + 'px';
        }
    });
/* 
    document.addEventListener('keydown', function(event) 
    {
        if (event.key === 'ArrowUp' || event.key === 'w')
            socket.send(JSON.stringify({ message: "flecha arriba" }));
        else if (event.key === 'ArrowDown' || event.key === 's')
            socket.send(JSON.stringify({ message: "flecha abajo" }));
    }); */

    // Manejar desconexión
    socket.onclose = function (event) {
        console.log("WebSocket desconectado");
    };

    // Manejar errores
    socket.onerror = function (error) {
        console.error("WebSocket error:", error);
    };
}