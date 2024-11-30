
// MATCH

function startGame()
{
    // PLAYER
    const socket = new WebSocket('ws://localhost:8000/ws/game/');
    
    // Escuchar eventos de conexión
    socket.onopen = function (event) {
        console.log("WebSocket conectado");
        socket.send(JSON.stringify({ message: "Hola desde el frontend" }));
    };
    
    // Escuchar mensajes desde el servidor
    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        //console.log("Mensaje recibido del servidor:", data.message);
        //console.log("player1 after:", data.player1, "player2 after:", data.player2);
        document.getElementById('left').style.marginTop = data.player1;
        document.getElementById('right').style.marginTop = data.player2;
    };

    // Manejar desconexión
    socket.onclose = function (event) {
        console.log("WebSocket desconectado");
    };

    // Manejar errores
    socket.onerror = function (error) {
        console.error("WebSocket error:", error);
    };

    
    const speed = 5;
    const table = document.getElementById('table');
    const playerHeight = document.getElementById('left').getBoundingClientRect().height;
    //console.log("height", playerHeight);
    const maxY = table.getBoundingClientRect().height;
    const minY = 0;
    document.addEventListener('keydown', function(event)
    {
        var dir1 = 0;
        const player1 = document.getElementById('left');
        const top1 = parseInt(window.getComputedStyle(player1).marginTop);
        var dir2 = 0;
        const player2 = document.getElementById('right');
        const top2 = parseInt(window.getComputedStyle(player2).marginTop);
        if (event.key === 'w' && top1 - speed > minY)
            dir1 = -1;
        else if (event.key === 's' && top1 + speed < maxY - playerHeight - 30)
            dir1 = 1;
        else if (event.key === 'ArrowUp' && top2 - speed > minY)
            dir2 = -1;
        else if (event.key === 'ArrowDown' && top2 + speed < maxY - playerHeight - 30)
            dir2 = 1;
        else
            return ;
        //console.log("player1 before:", (top1 + (dir1 * speed)) + 'px', "player2 before:", (top2 + (dir2 * speed)) + 'px');
        socket.send(JSON.stringify({
            message: (top1 + (dir1 * speed)) + 'px',
            player1: (top1 + (dir1 * speed)) + 'px',
            player2: (top2 + (dir2 * speed)) + 'px'
        }));
    });

    // SCORES
    var score1 = 0;
    var score2 = 0;
    
    // BALL
    var startBallY = parseInt(window.getComputedStyle(ball).top);
    var startBallX = parseInt(window.getComputedStyle(ball).left);
    
    // Tamaño del paso de movimiento y dirección inicial
    const ballSpeed = 1;
    let direccionX = ballSpeed;
    let direccionY = ballSpeed;
    
    function moverCirculo() {
        // Muestra el número en el contenedor
        document.getElementById('score1').textContent = score1;
        document.getElementById('score2').textContent = score2;
        
        const marginTable = 15;
        const ball = document.getElementById("ball");
        const table = document.getElementById('table');
        const player1 = document.getElementById('left');
        const player2 = document.getElementById('right');
        
        const minY = table.getBoundingClientRect().top + marginTable;
        const maxY = table.getBoundingClientRect().height - (2 * marginTable) + minY;
        const minX = table.getBoundingClientRect().left + marginTable;
        const maxX = table.getBoundingClientRect().width - (2 * marginTable) + minX;
        
        // const minY = parseInt(window.getComputedStyle(table).top) + marginTable;
        // const maxY = parseInt(window.getComputedStyle(table).height) - (2 * marginTable) + minY;
        // const minX = parseInt(window.getComputedStyle(table).left) + marginTable;
        // const maxX = parseInt(window.getComputedStyle(table).width) - (2 * marginTable) + minX;
        
        // Obtener posición actual
        // let topBall = ball.getBoundingClientRect().top;
        // let leftBall = ball.getBoundingClientRect().left;
        // let heightBall = ball.getBoundingClientRect().height;
        
        let topBall = parseInt(window.getComputedStyle(ball).top);
        let leftBall = parseInt(window.getComputedStyle(ball).left);
        let heightBall = parseInt(window.getComputedStyle(ball).height);
        let centerBall = topBall + (heightBall / 2);
        
        //let topPlayer = parseInt(window.getComputedStyle(player).top);
        let topPlayer1 = player1.getBoundingClientRect().top;
        let topPlayer2 = player2.getBoundingClientRect().top;
        
        // Calcular nuevas posiciones
        // console.log("dirX:", direccionY, "dirY:", direccionY);
        // console.log("leftBall:", leftBall, "topBall:", topBall);
        let newTop = topBall + direccionY;
        let newLeft = leftBall + direccionX;
        
        // Comprobar si el círculo ha tocado los bordes del contenedor
        if (newTop <= minY || newTop + ball.clientHeight >= maxY
        ) {// table.clientHeight) {
            direccionY *= -1; // Invertir la dirección en el eje Y
        }
        if ((newLeft <= minX + 20 &&
                centerBall > topPlayer1 && centerBall < topPlayer1 + playerHeight) ||
            (newLeft >= maxX - 20 &&
                centerBall > topPlayer2 && centerBall < topPlayer2 + playerHeight))
        {
            console.log("centerBall: " + centerBall);
            // console.log(", topPlayer: " + topPlayer);
            // console.log(", heightPlayer: " + (topPlayer + heightPlayer));
            // console.log("goal!!!!");
            direccionX *= -1;
        }
            // Aplicar nuevas posiciones
        ball.style.top = newTop + "px";
        ball.style.left = newLeft + "px";
        if (newLeft <= minX || newLeft + ball.clientWidth >= maxX) {// table.clientWidth) {
            direccionX *= -1; // Invertir la dirección en el eje X
            ball.style.top = startBallY + "px";
            ball.style.left = startBallX + "px";
            if (newLeft <= minX)
                score2++;
            else
                score1++;
        }
        if (score1 >= 10 || score2 >= 10)
            clearInterval(Match);
    }
    
    // Configurar el movimiento automático con setInterval
    let Match = setInterval(moverCirculo, 5); // Mueve el círculo cada 5ms
}
