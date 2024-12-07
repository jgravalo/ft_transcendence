
// MATCH

function startAsyncGame()
{
    // PLAYER
    const route = 'ws://' + base.slice(7) + ':8000/ws/game/async/';
    console.log('ruta: ', route);
    const socket = new WebSocket(route);
    
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
        /* document.getElementById('left').style.marginTop = data.player1;
        document.getElementById('right').style.marginTop = data.player2;
        var ball = document.getElementById('ball');
        ball.style.top = data.ballTop;
        ball.style.left = data.ballLeft; */
        console.log(data.message);
    };

    // Manejar desconexión
    socket.onclose = function (event) {
        console.log("WebSocket desconectado");
    };

    // Manejar errores
    socket.onerror = function (error) {
        console.error("WebSocket error:", error);
    };

}

function startGame()
{
    // PLAYER
    const route = 'ws://' + base.slice(7) + ':8000/ws/game/';
    console.log('ruta: ', route);
    const socket = new WebSocket(route);
    
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
        var ball = document.getElementById('ball');
        ball.style.top = data.ballTop;
        ball.style.left = data.ballLeft;
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
    var moveP1;
    var moveP2;
    var ballLeft;
    var ballTop;
    
    var dir1 = 0;
    var dir2 = 0;
    document.addEventListener('keyup', function(event)
    {
        if (event.key === 'w' || event.key === 's')
            dir1 = 0;
        else if (event.key === 'ArrowUp' || event.key === 'ArrowDown')
            dir2 = 0;
    });
    document.addEventListener('keydown', function(event)
    {
        const maxY = table.getBoundingClientRect().height;
        const minY = 0;
        const player1 = document.getElementById('left');
        const top1 = parseInt(window.getComputedStyle(player1).marginTop);
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
        moveP1 = (top1 + (dir1 * speed)) + 'px';
        moveP2 = (top2 + (dir2 * speed)) + 'px';
        /* socket.send(JSON.stringify({
            message: 'message',
            player1: moveP1,
            player2: moveP2
        })); */
    });
    
    // SCORES
    var score1 = 0;
    var score2 = 0;
    
    // BALL
    var startBallY = parseInt(window.getComputedStyle(ball).top);
    var startBallX = parseInt(window.getComputedStyle(ball).left);
    
    // Tamaño del paso de movimiento y dirección inicial
    const ballSpeed = 1;
    let dirBallX = ballSpeed;
    let dirBallY = ballSpeed;
    
    function moverCirculo()
    {
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
        
        let topBall = parseInt(window.getComputedStyle(ball).top);
        let leftBall = parseInt(window.getComputedStyle(ball).left);
        let heightBall = parseInt(window.getComputedStyle(ball).height);
        let centerBallY = topBall + (heightBall / 2);
        
        let topPlayer1 = player1.getBoundingClientRect().top;
        let topPlayer2 = player2.getBoundingClientRect().top;
        
        let newTop = topBall + dirBallY;
        let newLeft = leftBall + dirBallX;
        
        // Comprobar si el círculo ha tocado los bordes del contenedor
        if ((newTop <= minY || newTop + ball.clientHeight >= maxY))
            dirBallY *= -1; // Invertir la dirección en el eje Y
        /* if ((newLeft <= minX + 20 &&
                ((newTop + ball.clientHeight < topPlayer1 && centerBallY < topPlayer1) ||
                (newTop + ball.clientHeight > topPlayer1 + playerHeight && centerBallY < topPlayer1 + playerHeight))) ||
            (newLeft + heightBall >= maxX + 20 &&
                ((newTop + ball.clientHeight < topPlayer2 && centerBallY < topPlayer2) ||
                (newTop + ball.clientHeight > topPlayer2 + playerHeight && centerBallY < topPlayer2 + playerHeight))))
            dirBallY *= -1; // Invertir la dirección en el eje Y */
    
        if ((newLeft < minX + 20 &&
                centerBallY > topPlayer1 && centerBallY < topPlayer1 + playerHeight) ||
            (newLeft + heightBall > maxX - 20 &&
                centerBallY > topPlayer2 && centerBallY < topPlayer2 + playerHeight))
            dirBallX *= -1;
        // Aplicar nuevas posiciones
        // ball.style.top = newTop + "px";
        // ball.style.left = newLeft + "px";
        ballTop = newTop + "px";
        ballLeft = newLeft + "px";
        if (newLeft <= minX || newLeft + ball.clientWidth >= maxX)
        {
            dirBallX *= -1; // Invertir la dirección en el eje X
            // ball.style.top = startBallY + "px";
            // ball.style.left = startBallX + "px";
            ballTop = startBallY + "px";
            ballLeft = startBallX + "px";
            if (newLeft <= minX)
                score2++;
            else
                score1++;
        }
        socket.send(JSON.stringify({
            message: 'message',
            player1: moveP1,
            player2: moveP2,
            ballLeft: ballLeft,
            ballTop: ballTop
        }));
        if (score1 >= 10 || score2 >= 10)
        {
            document.getElementById('score1').textContent = score1;
            document.getElementById('score2').textContent = score2;
            clearInterval(Match);
        }
    }   
        // Configurar el movimiento automático con setInterval
    let Match = setInterval(moverCirculo, 5); // Mueve el círculo cada 5ms
}
            