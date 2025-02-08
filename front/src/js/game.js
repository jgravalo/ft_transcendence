/*
 * @section: Define variables and const to use along the game.
*/
const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');
canvas.width = 400;
canvas.height = 800;
ctx.fillStyle = '#000';
ctx.fillRect(0, 0, canvas.width, canvas.height);

/*
 * @section: Remote Mode:
 */
const socket = new WebSocket('ws://localhost:8000/ws/game/');

const remoteModeButton = document.getElementById('remote-mode');

remoteModeButton.addEventListener('click', () => {
    startRemoteGame();
});

function startRemoteGame() {
    console.log("🌐 Modo Remoto Activado");
    gameMode = "remote";

    document.getElementById("canvas-container").style.display = "block";
    document.getElementById("menu-message").innerText = "Conectando al servidor...";

    socket.onopen = () => {
        console.log("✅ Conectado al servidor WebSocket");

        // Esperar un pequeño tiempo antes de enviar el mensaje de unión para evitar desconexiones
        setTimeout(() => {
            socket.send(JSON.stringify({ type: 'join', player: 'player1' }));
        }, 500);
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("📩 Mensaje recibido:", data);

        if (data.type === 'waiting') {
            console.log("⌛ Esperando a otro jugador...");
            document.getElementById("menu-message").innerText = data.message;
        }

        if (data.type === 'start') {
            console.log("🚀 Juego comenzando...");
            document.getElementById("menu-message").innerText = data.message;
            isGameRunning = true;
            drawGame();
            gameLoop();
        }

        if (data.type === 'update') {
            console.log("🔄 Actualizando posiciones:", data.players);
            if (data.players['player1']) {
                player.x = data.players['player1'].x;
            }
            if (data.players['player2']) {
                ai.x = data.players['player2'].x;
            }
        }
    };

    socket.onclose = (event) => {
        console.warn("⚠ WebSocket cerrado:", event);
        if (event.code === 1001) {
            console.warn("⚠ La conexión fue cerrada inesperadamente. Posible problema en el backend.");
        }
    };
}






// @brief: Paddles sizes
const paddleWidth = 100, paddleHeight = 15;
const player = { x: canvas.width / 2 - paddleWidth / 2, y: canvas.height - 80, width: paddleWidth, height: paddleHeight, color: '#fff', powerUp: null, speedModifier: 1 };
const ai = { x: canvas.width / 2 - paddleWidth / 2, y: 60, width: paddleWidth, height: paddleHeight, color: '#fff', powerUp: null, speedModifier: 1 };

// @brief: Ball section
const ball = { x: canvas.width / 2, y: canvas.height / 2, size: 15, speedX: 4, speedY: 4, baseSpeed: 4, color: '#fff' };

// @brief: Power up section. Ready to include new power ups.
let powerUps = []; // Lista de power-ups activos
const powerUpSize = ball.size * 1.5; // 50% más grande que la pelota
let collisionCount = 0; // Contador de colisiones
const collisionThreshold = 5; // Número de colisiones para activar el power-up (ajustado para pruebas)
const activationDistance = powerUpSize * 3; // Distancia de activación
const powerUpColors = {
    '>>': 'green',
    '<<': 'red'
};
// @brief: min and max paddle size.
const minPaddleWidth = 45;
const maxPaddleWidth = canvas.width - 45;

// @brief Score
let playerScore = 0;
let aiScore = 0;

/*
 * @section: Values to ensure smooth move of paddles.
 * The Paddle accelerate and deccelerate depending of
 * how constant the key.
*/
let playerSpeed = 0;
const maxPlayerSpeed = 20;
const acceleration = 2;
const deceleration = 1;
let movingUp = false;
let movingDown = false;

let movingLeftPlayer = false;
let movingRightPlayer = false;
let movingLeftAi = false;
let movingRightAi = false;



// Movimiento de los jugadores
let aiSpeed = 0;
const maxSpeed = 20;


/*
 * @section: Game status
*/
let isGameRunning = false;
let gameWinner = null;
let gameMode = null;

/*
 * @section: Menu and buttons
*/
const menu = document.getElementById('game-menu');
const canvasContainer = document.getElementById('canvas-container');
const localModeButton = document.getElementById('local-mode');
const localAiModeButton = document.getElementById('local-ai-mode');


/*
 * @section: Menu listeners
*/

/*
 * @brief: Start a full local game (two players, one keyboard).
*/
localModeButton.addEventListener('click', () => {
    gameMode = 'local';
    startGame();
});

/*
 * @brief: Start a local game against a AI.
*/
localAiModeButton.addEventListener('click', () => {
    gameMode = 'local-ai';
    startGame();
});

/*
 * @brief: Controls the end of a given game. Close the pong interface
 * and back to the start screen.
 *
 * @param: winner. Player that win the game, to use it at winner message.
*/
function endGame(winner) {
    isGameRunning = false;
    menu.style.display = 'flex';
    canvasContainer.style.display = 'none';
    const message = winner === 'player' ? 'You win!' : 'You lost!';
    document.getElementById('menu-message').innerText = message;
}

/*
 * @brief: Start a game, starting the game loop.
 *
 * This method set the varibles needed to control the game,
 * and shows the canvas.
*/
function startGame() {
    isGameRunning = true;
    playerScore = 0;
    aiScore = 0;
    menu.style.display = 'none';
    canvasContainer.style.display = 'block';
    gameLoop();
}

/*
 * @brief: General function, draw a rectangle.
 *
 * @param: x x-pixel.
 * @param: y y-pixel.
 * @param: width of the rectangle.
 * @param: height of the rectangle.
 * @param: color of the rectangle.
*/
function drawRect(x, y, width, height, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, width, height);
}

/*
 * @brief: Draw dashed line at the middle of the field
 *
*/
function drawDashedLine() {
    ctx.strokeStyle = "#fff";
    ctx.setLineDash([15, 15]);
    ctx.lineWidth = 15;
    ctx.beginPath();
    ctx.moveTo(0, canvas.height / 2);
    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();
    ctx.setLineDash([]);
}

/*
 * @brief: Draw score
 *
*/
function drawScore() {
    ctx.font = "70px Silkscreen";
    ctx.fillStyle = "#fff";
    ctx.textAlign = "right";

    ctx.fillText(playerScore, canvas.width - 20, canvas.height / 2 + 140);
    ctx.fillText(aiScore, canvas.width - 20, canvas.height / 2 - 100);
}

/*
 * @brief: Draw power ups.
*/
function drawPowerUps() {
    for (const powerUp of powerUps) {
        ctx.fillStyle = powerUpColors[powerUp.type];
        ctx.font = '20px Silkscreen';
        ctx.textAlign = 'center';
        ctx.fillText(powerUp.type, powerUp.x + powerUpSize / 2, powerUp.y + powerUpSize / 1.5);
        drawRect(powerUp.x, powerUp.y, powerUpSize, powerUpSize, powerUpColors[powerUp.type]);
    }
}

/*
 * @brief: Move power ups function.
*/
function movePowerUps() {
    for (let i = powerUps.length - 1; i >= 0; i--) {
        const powerUp = powerUps[i];
        powerUp.y += powerUp.speedY;
        powerUp.x += powerUp.speedX;

        if (powerUp.x + powerUpSize > canvas.width || powerUp.x < 0) {
            powerUp.speedX = -powerUp.speedX;
        }

        if (powerUp.y > canvas.height || powerUp.y < 0) {
            console.log("Power-Up perdido!");
            powerUps.splice(i, 1);
        }
    }
}

/*
 * @brief: Generate a random power when collision counter
 * arrives to collisionThreshold value.
*/
function generatePowerUp() {
    if (collisionCount >= collisionThreshold && powerUps.length === 0) {
        console.log("Generando Power-Up..."); // Depuración
        const fromPlayer = Math.random() > 0.5;
        const paddle = fromPlayer ? player : ai;
        const directionY = fromPlayer ? -3 : 3;
        const directionX = (Math.random() - 0.5) * 2;
        const types = ['>>', '<<']; // Lista inicial de power-ups
        const type = types[Math.floor(Math.random() * types.length)];
        powerUps.push({
            x: paddle.x + paddle.width / 2 - powerUpSize / 2,
            y: paddle.y,
            startY: paddle.y,
            speedY: directionY,
            speedX: directionX,
            type,
            active: false
        });
        collisionCount = 0;
    }
}

/*
 * @brief: Apply power up after it is cought by a paddle.
 *
 * @param: player that cought the power up.
 * @param: powerUpType Power up that was cought.
*/
function applyPowerUp(player, powerUpType) {
    if (powerUpType === '>>') {
        // Incrementa el tamaño, respetando el límite máximo
        player.width = Math.min(player.width + 10, maxPaddleWidth);
        player.speedModifier = Math.max(player.speedModifier - 0.1, 0.8); // Reduce la velocidad al aumentar el tamaño
        player.powerUp = '>>';
    } else if (powerUpType === '<<') {
        // Reduce el tamaño, respetando el límite mínimo
        player.width = Math.max(player.width - 10, minPaddleWidth);
        player.speedModifier = Math.min(player.speedModifier + 0.1, 1.2); // Aumenta la velocidad al reducir el tamaño
        player.powerUp = '<<';
    }
}

/*
 * @brief: Reset Power Up. Reroll power up.
*/
function resetPowerUp(player) {
    player.powerUp = null;
    player.speedModifier = 1;
}

/*
 * @brief: Move ball function.
 *
 * This function move the ball, and control collisions.
*/
function moveBall() {
    ball.x += ball.speedX;
    ball.y += ball.speedY;

    // Border collision to avoid 'trapped' behaviour.
    if (ball.x - ball.size / 2 <= 0) {
        ball.x = ball.size / 2;
        // The ball speed is modify by the power up, if applies.
        ball.speedX = Math.abs(ball.baseSpeed * player.speedModifier);
        collisionCount++;
    }
    if (ball.x + ball.size / 2 >= canvas.width) {
        ball.x = canvas.width - ball.size / 2;
        ball.speedX = -Math.abs(ball.baseSpeed * ai.speedModifier); // Ajustar según el modificador de la IA
        collisionCount++;
    }

    if (ball.y - ball.size / 2 <= 0) {
        playerScore++;
        resetBall();
    } else if (ball.y + ball.size / 2 >= canvas.height) {
        aiScore++;
        resetBall();
    }

    // Paddle collisions
    if (checkCollision(ball, player)) {
        ball.y = player.y - ball.size / 2;
        ball.speedY = -Math.abs(ball.baseSpeed * player.speedModifier); // Aplica el modificador pero reinicia el cálculo base
    } else if (checkCollision(ball, ai)) {
        ball.y = ai.y + ai.height + ball.size / 2;
        ball.speedY = Math.abs(ball.baseSpeed * ai.speedModifier); // Aplica el modificador pero reinicia el cálculo base
    }

    generatePowerUp();
}

/*
 * @brief: Reset Ball when it get lost by the end of the field.
 *
 * Position and angle of first deliver is random, and collision count (for power ups)
 * is back to 0.
*/
function resetBall() {
    ball.x = canvas.width / 2;
    ball.y = canvas.height / 2;
    const angle = (Math.random() - 0.5) * Math.PI / 8;
    ball.speedX = ball.baseSpeed * Math.sin(angle);
    ball.speedY = ball.baseSpeed * Math.cos(angle) * (Math.random() > 0.5 ? 1 : -1);
    collisionCount = 0;
}

/*
 * @brief: Move AI
*/
function moveAI() {
    const centerAI = ai.x + ai.width / 2;

    if (centerAI < ball.x - 10) {
        ai.x += 3;
    } else if (centerAI > ball.x + 10) {
        ai.x -= 3;
    }

    ai.x = Math.max(0, Math.min(ai.x, canvas.width - ai.width));
}

/*
 * @brief: Check ball - paddle collision.
 *
 * @param: ball. Ball object.
 * @param: paddle. Paddle object.
*/
function checkCollision(ball, paddle) {
    const collision =
        ball.x > paddle.x &&
        ball.x < paddle.x + paddle.width &&
        ball.y + ball.size / 2 > paddle.y &&
        ball.y - ball.size / 2 < paddle.y + paddle.height;

    if (collision) {
        const hitPoint = ball.x - (paddle.x + paddle.width / 2);
        const normalizedHitPoint = hitPoint / (paddle.width / 2);
        ball.speedX = normalizedHitPoint * 6;
    }

    return collision;
}

/*
 * @brief: Check Power Up Collision.
 *
 * This method check the power up collision with borders, ball and paddle.
 * TODO: Some logs should be deleted, included for dev pourpose.
*/
function checkPowerUpCollisions() {
    for (let i = powerUps.length - 1; i >= 0; i--) {
        const powerUp = powerUps[i];
        const distance = Math.abs(powerUp.startY - powerUp.y);
        powerUp.active = distance >= activationDistance;

        if (!powerUp.active) continue;

        if (
            ball.x < powerUp.x + powerUpSize &&
            ball.x + ball.size > powerUp.x &&
            ball.y < powerUp.y + powerUpSize &&
            ball.y + ball.size > powerUp.y
        ) {
            ball.speedY = -ball.speedY;
            ball.speedX = -ball.speedX;
            console.log("¡Power-Up impactado por la pelota!");
            powerUps.splice(i, 1);
            continue;
        }

        if (
            powerUp.x < player.x + player.width &&
            powerUp.x + powerUpSize > player.x &&
            powerUp.y < player.y + player.height &&
            powerUp.y + powerUpSize > player.y
        ) {
            console.log("Power-Up capturado por el jugador!");
            applyPowerUp(player, powerUp.type);
            powerUps.splice(i, 1);
        } else if (
            powerUp.x < ai.x + ai.width &&
            powerUp.x + powerUpSize > ai.x &&
            powerUp.y < ai.y + ai.height &&
            powerUp.y + powerUpSize > ai.y
        ) {
            console.log("Power-Up capturado por la IA!");
            applyPowerUp(ai, powerUp.type);
            powerUps.splice(i, 1);
        }
    }
}

/*
 * @brief: Update Game
 *
 * Update game, after a point is scored.
*/
function updateGame() {
    if (!isGameRunning) return;

    movePlayer();

    if (gameMode === 'local') {
        movePlayerTwo();
    } else if (gameMode === 'local-ai') {
        moveAI();
    }

    moveBall();
    movePowerUps();
    checkPowerUpCollisions();

    if (playerScore >= 5) {
        endGame('player');
    } else if (aiScore >= 5) {
        endGame('ai');
    }
}

/*
 * @brief: Move main player
 *
 * Main player is the one that is show at the botton of the field.
*/
function movePlayer() {
    if (movingLeftPlayer) {
        playerSpeed = Math.min(playerSpeed + acceleration, maxSpeed);
        player.x -= playerSpeed;
    } else if (movingRightPlayer) {
        playerSpeed = Math.min(playerSpeed + acceleration, maxSpeed);
        player.x += playerSpeed;
    } else {
        playerSpeed = Math.max(playerSpeed - deceleration, 0);
    }

    player.x = Math.max(0, Math.min(player.x, canvas.width - player.width));
}

/*
 * @brief: Move Player Two
 *
 * Player two is defined as the top one.
 * TODO: Player two is local so far. This method should be fixed
 * when remote player is implemented.
*/
function movePlayerTwo() {
    if (movingLeftAi) {
        aiSpeed = Math.min(aiSpeed + acceleration, maxSpeed);
        ai.x -= aiSpeed;
    } else if (movingRightAi) {
        aiSpeed = Math.min(aiSpeed + acceleration, maxSpeed);
        ai.x += aiSpeed;
    } else {
        aiSpeed = Math.max(aiSpeed - deceleration, 0);
    }

    ai.x = Math.max(0, Math.min(ai.x, canvas.width - ai.width));
}

// Listeners para el control de ambos jugadores
document.addEventListener('keydown', (e) => {
    let movement = 0;

    if (e.key === 'ArrowLeft') movement = -10;
    if (e.key === 'ArrowRight') movement = 10;

    if (movement !== 0) {
        player.x = Math.max(0, Math.min(player.x + movement, canvas.width - player.width));
        console.log(`⬅➡ Movimiento local: ${player.x}`);

        // 🏓 Si estamos en modo remoto, enviamos el movimiento al WebSocket
        if (gameMode === 'remote' && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: "move", player: "player1", x: player.x }));
        }
    }
});

document.addEventListener('keyup', (e) => {
    if (e.key === 'ArrowLeft') movingLeftPlayer = false;
    if (e.key === 'ArrowRight') movingRightPlayer = false;
    if (e.key === 'a') movingLeftAi = false;
    if (e.key === 'd') movingRightAi = false;
});



/*
 * @brief: Draw Game.
 *
 * Make the game elements visibles, draw the field, paddles
 * and score
*/
function drawGame() {
    if (!isGameRunning) return;

    drawRect(0, 0, canvas.width, canvas.height, '#000');
    drawDashedLine();
    drawRect(player.x, player.y, player.width, player.height, player.color);
    drawRect(ai.x, ai.y, ai.width, ai.height, ai.color);
    drawRect(ball.x - ball.size / 2, ball.y - ball.size / 2, ball.size, ball.size, ball.color);
    drawPowerUps();
    drawScore();
}

/*
 * @brief: Game loop
 *
 * Game loop start the game workflow.
*/
function gameLoop() {
    if (isGameRunning) {
        console.log("Game Loop");
        updateGame();
        drawGame();
        requestAnimationFrame(gameLoop);
    }
}

/*
 * @section: Main screen.
 *
 * Show the main screen to start the game workflow.
*/
menu.style.display = 'flex';
canvasContainer.style.display = 'none';



//
// // MATCH
//
// function startAsyncGame()
// {
//     // PLAYER
//     const route = 'ws://' + base.slice(7) + '/ws/game/async/';
//     console.log('ruta: ', route);
//     const socket = new WebSocket(route);
//
//     // Escuchar eventos de conexión
//     socket.onopen = function (event) {
//         console.log("WebSocket conectado");
//         socket.send(JSON.stringify({ message: "Hola desde el frontend" }));
//     };
//
//     // Escuchar mensajes desde el servidor
//     socket.onmessage = function (event) {
//         const data = JSON.parse(event.data);
//         //console.log("Mensaje recibido del servidor:", data.message);
//         //console.log("player1 after:", data.player1, "player2 after:", data.player2);
//         /* document.getElementById('left').style.marginTop = data.player1;
//         document.getElementById('right').style.marginTop = data.player2;
//         var ball = document.getElementById('ball');
//         ball.style.top = data.ballTop;
//         ball.style.left = data.ballLeft; */
//         console.log(data.message);
//     };
//
//     // Manejar desconexión
//     socket.onclose = function (event) {
//         console.log("WebSocket desconectado");
//     };
//
//     // Manejar errores
//     socket.onerror = function (error) {
//         console.error("WebSocket error:", error);
//     };
//
// }
//
// function startGame()
// {
//     // PLAYER
//     const route = 'ws://' + base.slice(7) + '/ws/game/';
//     console.log('ruta: ', route);
//     const socket = new WebSocket(route);
//
//     // Escuchar eventos de conexión
//     socket.onopen = function (event) {
//         console.log("WebSocket conectado");
//         socket.send(JSON.stringify({ message: "Hola desde el frontend" }));
//     };
//
//     // Escuchar mensajes desde el servidor
//     socket.onmessage = function (event) {
//         const data = JSON.parse(event.data);
//         //console.log("Mensaje recibido del servidor:", data.message);
//         //console.log("player1 after:", data.player1, "player2 after:", data.player2);
//         document.getElementById('left').style.marginTop = data.player1;
//         document.getElementById('right').style.marginTop = data.player2;
//         var ball = document.getElementById('ball');
//         ball.style.top = data.ballTop;
//         ball.style.left = data.ballLeft;
//     };
//
//     // Manejar desconexión
//     socket.onclose = function (event) {
//         console.log("WebSocket desconectado");
//     };
//
//     // Manejar errores
//     socket.onerror = function (error) {
//         console.error("WebSocket error:", error);
//     };
//
//     const speed = 5;
//     const table = document.getElementById('table');
//     const playerHeight = document.getElementById('left').getBoundingClientRect().height;
//     var moveP1;
//     var moveP2;
//     var ballLeft;
//     var ballTop;
//
//     var dir1 = 0;
//     var dir2 = 0;
//     document.addEventListener('keyup', function(event)
//     {
//         if (event.key === 'w' || event.key === 's')
//             dir1 = 0;
//         else if (event.key === 'ArrowUp' || event.key === 'ArrowDown')
//             dir2 = 0;
//     });
//     document.addEventListener('keydown', function(event)
//     {
//         const maxY = table.getBoundingClientRect().height;
//         const minY = 0;
//         const player1 = document.getElementById('left');
//         const top1 = parseInt(window.getComputedStyle(player1).marginTop);
//         const player2 = document.getElementById('right');
//         const top2 = parseInt(window.getComputedStyle(player2).marginTop);
//         if (event.key === 'w' && top1 - speed > minY)
//             dir1 = -1;
//         else if (event.key === 's' && top1 + speed < maxY - playerHeight - 30)
//             dir1 = 1;
//         else if (event.key === 'ArrowUp' && top2 - speed > minY)
//             dir2 = -1;
//         else if (event.key === 'ArrowDown' && top2 + speed < maxY - playerHeight - 30)
//             dir2 = 1;
//         else
//             return ;
//         //console.log("player1 before:", (top1 + (dir1 * speed)) + 'px', "player2 before:", (top2 + (dir2 * speed)) + 'px');
//         moveP1 = (top1 + (dir1 * speed)) + 'px';
//         moveP2 = (top2 + (dir2 * speed)) + 'px';
//         /* socket.send(JSON.stringify({
//             message: 'message',
//             player1: moveP1,
//             player2: moveP2
//         })); */
//     });
//
//
//     // SCORES
//     var score1 = 0;
//     var score2 = 0;
//
//     // BALL
//     var startBallY = parseInt(window.getComputedStyle(ball).top);
//     var startBallX = parseInt(window.getComputedStyle(ball).left);
//
//     // Tamaño del paso de movimiento y dirección inicial
//     const ballSpeed = 1;
//     let dirBallX = ballSpeed;
//     let dirBallY = ballSpeed;
//
//     document.getElementById('offline-button').addEventListener('click', () => {
//         clearInterval(Match); // Detener el intervalo
//         ball.style.top = startBallY + "px";
//         ball.style.left = startBallX + "px";
//         console.log('Intervalo detenido');
//     });
//
//     function moverCirculo()
//     {
//         // Muestra el número en el contenedor
//         document.getElementById('score1').textContent = score1;
//         document.getElementById('score2').textContent = score2;
//
//         const marginTable = 15;
//         const ball = document.getElementById("ball");
//         const table = document.getElementById('table');
//         const player1 = document.getElementById('left');
//         const player2 = document.getElementById('right');
//
//         const minY = table.getBoundingClientRect().top + marginTable;
//         const maxY = table.getBoundingClientRect().height - (2 * marginTable) + minY;
//         const minX = table.getBoundingClientRect().left + marginTable;
//         const maxX = table.getBoundingClientRect().width - (2 * marginTable) + minX;
//
//         let topBall = parseInt(window.getComputedStyle(ball).top);
//         let leftBall = parseInt(window.getComputedStyle(ball).left);
//         let heightBall = parseInt(window.getComputedStyle(ball).height);
//         let centerBallY = topBall + (heightBall / 2);
//
//         let topPlayer1 = player1.getBoundingClientRect().top;
//         let topPlayer2 = player2.getBoundingClientRect().top;
//
//         let newTop = topBall + dirBallY;
//         let newLeft = leftBall + dirBallX;
//
//         // Comprobar si el círculo ha tocado los bordes del contenedor
//         if ((newTop <= minY || newTop + ball.clientHeight >= maxY))
//             dirBallY *= -1; // Invertir la dirección en el eje Y
//         /* if ((newLeft <= minX + 20 &&
//                 ((newTop + ball.clientHeight < topPlayer1 && centerBallY < topPlayer1) ||
//                 (newTop + ball.clientHeight > topPlayer1 + playerHeight && centerBallY < topPlayer1 + playerHeight))) ||
//             (newLeft + heightBall >= maxX + 20 &&
//                 ((newTop + ball.clientHeight < topPlayer2 && centerBallY < topPlayer2) ||
//                 (newTop + ball.clientHeight > topPlayer2 + playerHeight && centerBallY < topPlayer2 + playerHeight))))
//             dirBallY *= -1; // Invertir la dirección en el eje Y */
//
//         if ((newLeft < minX + 20 &&
//                 centerBallY > topPlayer1 && centerBallY < topPlayer1 + playerHeight) ||
//             (newLeft + heightBall > maxX - 20 &&
//                 centerBallY > topPlayer2 && centerBallY < topPlayer2 + playerHeight))
//             dirBallX *= -1;
//         // Aplicar nuevas posiciones
//         // ball.style.top = newTop + "px";
//         // ball.style.left = newLeft + "px";
//         ballTop = newTop + "px";
//         ballLeft = newLeft + "px";
//         if (newLeft <= minX || newLeft + ball.clientWidth >= maxX)
//         {
//             dirBallX *= -1; // Invertir la dirección en el eje X
//             // ball.style.top = startBallY + "px";
//             // ball.style.left = startBallX + "px";
//             ballTop = startBallY + "px";
//             ballLeft = startBallX + "px";
//             if (newLeft <= minX)
//                 score2++;
//             else
//                 score1++;
//         }
//         socket.send(JSON.stringify({
//             message: 'message',
//             player1: moveP1,
//             player2: moveP2,
//             ballLeft: ballLeft,
//             ballTop: ballTop
//         }));
//         if (score1 >= 5 || score2 >= 5)
//         {
//             document.getElementById('score1').textContent = score1;
//             document.getElementById('score2').textContent = score2;
//             socket.close(1000, 'Finalizando conexión de manera ordenada');
//             clearInterval(Match);
//         }
//     }
//         // Configurar el movimiento automático con setInterval
//     let Match = setInterval(moverCirculo, 5); // Mueve el círculo cada 5ms
// }
//