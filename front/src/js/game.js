/*
 * @section: Define variables and const to use along the game.
*/
const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');
canvas.width = 400;
canvas.height = 800;
ctx.fillStyle = '#000';
ctx.fillRect(0, 0, canvas.width, canvas.height);

// @brief: Paddles sizes
const paddleWidth = 100, paddleHeight = 15;
const player = {
    speed: 0,
    x: canvas.width / 2 - paddleWidth / 2,
    y: canvas.height - 80, width: paddleWidth,
    height: paddleHeight,
    color: '#fff',
    powerUp: null,
    speedModifier: 1
};
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
const remoteMode = document.getElementById('remote-mode');
const playerName = document.getElementById('playerName').textContent;

// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> REMOTE

/*
 * @section: Remote Mode
 */


function remoteModeGame() {
    const socket = new WebSocket('ws://localhost:8000/ws/game/');
    let playerId = null; // ID del jugador asignado por el servidor
    let hasGameStarted = false; // Flag para asegurarnos de que el juego inicia correctamente
    isGameRunning = true;
    playerScore = 0;
    aiScore = 0;
    // menu.style.display = 'none';
    canvasContainer.style.display = 'block';
    socket.onopen = () => {
        console.log("✅ Conectado al servidor WebSocket");

        // Enviar solicitud de unión al juego
        socket.send(JSON.stringify({ step: 'join', username: playerName, game_mode: 'remote-ia'}));

        // Mostrar el canvas
        document.getElementById("canvas-container").style.display = "block";
        document.getElementById("menu-message").innerText = "Esperando respuesta del servidor...";
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("📩 Mensaje recibido:", data);
        if (data.step === 'wait') {
            document.getElementById("menu-message").innerText = data.player_id;
        }
        if (data.step === 'update') {
            console.log("🔄 Recibida actualización de posiciones:", data.players);

            if (!playerId) {
                playerId = data.players.hasOwnProperty("player1") ? "player1" : "player2";
                console.log(`🎮 Jugador asignado: ${playerId}`);
            }

            const opponentId = playerId === "player1" ? "player2" : "player1";

            if (data.players[playerId]) {
                player.x = data.players[playerId].x;
            }
            if (data.players[opponentId]) {
                ai.x = data.players[opponentId].x;
            }

            // 🏓 Asegurar que el juego se dibuje
            if (!hasGameStarted) {
                hasGameStarted = true;
                isGameRunning = true;
                document.getElementById("menu-message").innerText = "Juego en marcha!";
                drawGame();
                gameLoop();
            }
        }
    };
}

// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> REMOTE
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

remoteMode.addEventListener('click', () => {
    gameMode = 'remote-mode';
    remoteModeGame();
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

    playerSpeed = movePaddle(player, movingLeftPlayer, movingRightPlayer, playerSpeed);

    if (gameMode === 'local-ai') {
        moveAI();
        aiSpeed = movePaddle(ai, movingLeftAi, movingRightAi, aiSpeed);
    } else if (gameMode === 'local') {
        aiSpeed = movePaddle(ai, movingLeftAi, movingRightAi, aiSpeed);
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

function movePaddle(paddle, movingLeft, movingRight, speed) {
    if (movingLeft) {
        speed = Math.min(speed + acceleration, maxSpeed);
        paddle.x -= speed;
    } else if (movingRight) {
        speed = Math.min(speed + acceleration, maxSpeed);
        paddle.x += speed;
    } else {
        speed = Math.max(speed - deceleration, 0);
    }

    paddle.x = Math.max(0, Math.min(paddle.x, canvas.width - paddle.width));

    return speed;
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
    if (e.key === 'ArrowLeft') movingLeftPlayer = true;
    if (e.key === 'ArrowRight') movingRightPlayer = true;
    if (e.key === 'a') movingLeftAi = true;
    if (e.key === 'd') movingRightAi = true;
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
