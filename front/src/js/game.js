
function game()
{
    /*
    * @brief: Listener to open game menu inside the game canvas.
    *
    * When a user clicks over the auto-play game, the menu is shown.
    */
    document.getElementById("pongCanvas").addEventListener("click", function (event) {
        if (gameMode === "auto-play") {
            const menu = document.getElementById("overlay");
            const canvas = this.getBoundingClientRect();

            menu.style.width = `${canvas.width}px`;
            menu.style.height = `${canvas.height}px`;
            menu.style.top = `${canvas.top}px`;
            menu.style.left = `${canvas.left}px`;
            menu.style.display = "flex";
        }
    });

    /*
    * @brief: Listener to close game menu.
    *
    * When a user clicks outside the game canvas, game menu is closed.
    */
    document.addEventListener("click", function (event) {
        const menu = document.getElementById("overlay");
        const canvas = document.getElementById("pongCanvas");

        if (menu.style.display === "flex" && !canvas.contains(event.target) && !menu.contains(event.target)) {
            menu.style.display = "none";
        }
    });

    /*
    * @brief: Set up a game mode and start game workflow.
    */
    function setGameMode(mode) {
        document.getElementById("overlay").style.display = "none";
        gameMode = mode;
        resetGameData();
        if (mode === "local") {
            playerName = "player1";
            opponentName = "player2";
            startGame();
        } else if (mode === "remote") {
            remoteModeGame();
        } else if (mode === "remote-ai") {
            remoteModeGame();
        }
    }

    /*
    * @section: HTML elements to catch and use.
    *
    *   pongCanvas: to draw the game.
    *   ctx: to use context if is necessary.
    *   set the size of the game.
    */
    const canvas = document.getElementById('pongCanvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 400;
    canvas.height = 800;
    ctx.fillStyle = '#1b2735';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    // const menu = document.getElementById('game-menu');
    const canvasContainer = document.getElementById('canvas-container');
// TODO: User name should be placed properly
    // const playerName = document.getElementById('playerName').textContent;

    /*
    * @brief: General function to draw a rectangle.
    *
    * @param {x}: x position of the rectangle.
    * @param {y}: y position of the rectangle.
    * @param {width}: width of the rectangle.
    * @param {height}: height of the rectangle.
    * @param {color}: color of the rectangle.
    */
    function drawRect(x, y, width, height, color) {
        ctx.fillStyle = color;
        ctx.fillRect(x, y, width, height);
    }

    /*
    * @section: Drawers.
    *
    * drawDashedLine: Draw the middle line of the game.
    * drawScore: Draw the score of the current game.
    * drawPowerUps: Draw the generated Power Ups.
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

    function drawPlayerName() {
        ctx.font = "40px Silkscreen";
        ctx.fillStyle = "#fff";
        ctx.textAlign = "left";
        ctx.fillText(playerName, 0, canvas.height - 5);
    }

    function drawOpponentName() {
        ctx.font = "40px Silkscreen";
        ctx.fillStyle = "#fff";
        ctx.textAlign = "right";
        ctx.fillText(opponentName, canvas.width, 35);
    }

    function drawMessage(announce) {
        drawRect(0, 0, canvas.width, canvas.height, '#000');
        ctx.font = "30px Silkscreen";
        ctx.fillStyle = "#fff";
        ctx.textAlign = "center";
        ctx.fillText(announce, canvas.width / 2, canvas.height / 2 + 70, canvas.width - 10);
    }

    function drawScore() {
        ctx.font = "70px Silkscreen";
        ctx.fillStyle = "#fff";
        ctx.textAlign = "right";

        ctx.fillText(player.score, canvas.width - 20, canvas.height / 2 + 140);
        ctx.fillText(opponent.score, canvas.width - 20, canvas.height / 2 - 100);
    }

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
    * @section: Helpers to restart game data.
    */
    function resetGameData(){
        const player_y = canvas.height - 80;
        const opponent_y = 60;
        const base_player = {
            playerName: playerName,
            left: false,
            right: false,
            x: canvas.width / 2 - paddleWidth / 2,
            width: paddleWidth,
            height: paddleHeight,
            color: '#fff',
            powerUp: null,
            score: 0,
            points: 0,
            speed: 0,
            speedModifier: 1
        };
        Object.assign(player, base_player);
        Object.assign(opponent, base_player);
        player.y = player_y;
        opponent.y = opponent_y;
    }



// ---------------------------------------------------------------------

    /*
    * @section: Variables and objects used through the game workflow
    *
    * Paddle Sizes.
    * Player Object.
    * Opponent Object.
    * Ball ...
    * @TODO: Complete comment
    * */
    const paddleWidth = 100
    const paddleHeight = 15;
    const minPaddleWidth = 45;
    const maxPaddleWidth = canvas.width - 45;
    const acceleration = 2;
    const deceleration = 1;
    const maxSpeed = 20;
    let isGameRunning = false;
    let gameWinner = null;
    let gameMode = null;
    let playerName = "player1"
    let opponentName = "player2";
    let fieldMessage = "Click to play!"

    const player = {
        playerName: playerName,
        role: 'player1',
        left: false,
        right: false,
        x: canvas.width / 2 - paddleWidth / 2,
        y: canvas.height - 80,
        width: paddleWidth,
        height: paddleHeight,
        color: '#4ac1f7',
        powerUp: null,
        score: 0,
        points: 0,
        speed: 0,
        speedModifier: 1
    };

    const opponent = {
        playerName: opponentName,
        role: 'player2',
        left: false,
        right: false,
        x: canvas.width / 2 - paddleWidth / 2,
        y: 60,
        width: paddleWidth,
        height: paddleHeight,
        color: '#fff',
        powerUp: null,
        score: 0,
        points: 0,
        speed: 0,
        speedModifier: 1
    };

    const ball = {
        x: canvas.width / 2,
        y: canvas.height / 2,
        size: 15,
        speedX: 4,
        speedY: 4,
        baseSpeed: 4,
        color: '#fff'
    };

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

// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> REMOTE

    /*
     * @section: Remote Mode
     */
    let socket = null;
    function connect() {
        if (gameMode === 'remote-ai') {
            socket = new WebSocket('ws://localhost:8000/ws/gamehal/');
        } else {
            socket = new WebSocket('ws://localhost:8000/ws/game/');
        }
    }

    function remoteModeGame() {
        connect();
        canvasContainer.style.display = 'block';

        socket.onopen = () => {
            // Join to remote game
            socket.send(JSON.stringify({
                step: 'join',
                username: playerName,
                player: player,
                mode: gameMode}
            ));

            document.getElementById("canvas-container").style.display = "block";
            document.getElementById("menu-message").innerText = "Esperando respuesta del servidor...";
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.step === 'wait') {
                resetBall();
                playerName = data.playerName;
                waitingLoop('Waiting for a victim!');
            } else if (data.step === 'ready') {
                if (data.playerRole === 'player1') {
                    Object.assign(player, data.player1);
                    playerName = player.playerName;
                    opponentName = data.opponentName;
                } else {
                    Object.assign(player, data.player2);
                    playerName = data.opponentName;
                    opponentName = player.playerName;
                }
                startingLoop(data.message);
            } else if (data.step === 'start') {
                opponentName = data.opponentName;
                opponent.playerName = data.opponentName;
                startGame();
            } else if (data.step === 'go') {
                if (player.role === 'player1') {
                    Object.assign(opponent, data.player2);
                    Object.assign(player, data.player1);
                } else {
                    Object.assign(opponent, data.player1);
                    Object.assign(player, data.player2);
                }
                Object.assign(ball, data.ball);
                playerName = data.player1Name;
                opponentName = data.player2Name;
                isGameRunning = true;
                gameLoop()
            } else if (data.step === 'move') {
                opponent.x = data.position;
            } else if (data.step === 'update') {
                Object.assign(opponent, data.opponent);
                Object.assign(player, data.player);
                Object.assign(ball, data.ball);
                powerUps = data.powerUps;
            } else if (data.step === 'join-ia') {
                socket.send(JSON.stringify({
                    step: 'start',
                    player: player,
                    opponent: opponent,
                    ball: ball,
                    canvas: canvas }
                ));
            }
        };
    }



    function listener() {
        if (gameMode === 'remote-ai') {
            socket.send(JSON.stringify({
                'step': 'move',
                'position': opponent,
                'ball': ball
            }))
        } else {
            socket.send(JSON.stringify({
                'step': 'update',
                'role': player.role,
                'position': player.x
            }))
        }

    }

    /*
    * @section: Game related functions.
    *
    *
    */

    function endGame(winner) {
        isGameRunning = false;
        // menu.style.display = 'flex';
        // canvasContainer.style.display = 'none';
        if (gameMode === 'remote-ai') {
            socket.send(JSON.stringify({
                'step': 'end',
                'player_score': player.score,
                'opponent_score': opponent.score
            }))
        }
        autoPlay(winner);
    }

    function startGame() {
        isGameRunning = true;
        player.score = 0;
        opponent.score = 0;
        canvasContainer.style.display = 'block';
        gameLoop();
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
            const fromPlayer = Math.random() > 0.5;
            const paddle = fromPlayer ? player : opponent;
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
     * @brief: Move ball function.
     *
     * This function move the ball, and control collisions.
    */
    function moveBall() {
        ballPlay();
        if (ball.y - ball.size / 2 <= 0) {
            player.score++;
            resetBall();
        } else if (ball.y + ball.size / 2 >= canvas.height) {
            opponent.score++;
            resetBall();
        }

        // Paddle collisions
        if (checkCollision(ball, player)) {
            ball.y = player.y - ball.size / 2;
            ball.speedY = -Math.abs(ball.baseSpeed * player.speedModifier);
        } else if (checkCollision(ball, opponent)) {
            ball.y = opponent.y + opponent.height + ball.size / 2;
            ball.speedY = Math.abs(ball.baseSpeed * opponent.speedModifier);
        }
        generatePowerUp();
    }

    function ballPlay() {
        ball.x += ball.speedX;
        ball.y += ball.speedY;

        // Border collision to avoid 'trapped' behaviour.
        if (ball.x - ball.size / 2 <= 0) {
            ball.x = ball.size / 2;
            ball.speedX = Math.abs(ball.baseSpeed * player.speedModifier);
            collisionCount++;
        }
        if (ball.x + ball.size / 2 >= canvas.width) {
            ball.x = canvas.width - ball.size / 2;
            ball.speedX = -Math.abs(ball.baseSpeed * opponent.speedModifier);
        }
    }

    function ballBounce() {
        if (ball.y - ball.size <= 0) {
            ball.y = ball.size;
            ball.speedY = Math.abs(ball.baseSpeed);
        } else if (ball.y + ball.size >= canvas.height) {
            ball.y = canvas.height - ball.size;
            ball.speedY = -Math.abs(ball.baseSpeed);
        }
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
                powerUps.splice(i, 1);
                continue;
            }

            if (
                powerUp.x < player.x + player.width &&
                powerUp.x + powerUpSize > player.x &&
                powerUp.y < player.y + player.height &&
                powerUp.y + powerUpSize > player.y
            ) {
                applyPowerUp(player, powerUp.type);
                powerUps.splice(i, 1);
            } else if (
                powerUp.x < opponent.x + opponent.width &&
                powerUp.x + powerUpSize > opponent.x &&
                powerUp.y < opponent.y + opponent.height &&
                powerUp.y + powerUpSize > opponent.y
            ) {
                applyPowerUp(opponent, powerUp.type);
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
        movePaddle(player);

        if (gameMode === 'local') {
            movePaddle(opponent);
        } else if (gameMode === 'remote-ai') {
            listener();
            movePaddle(opponent);
        }
        if (gameMode !== 'remote') {
            moveBall();
            movePowerUps();
            checkPowerUpCollisions();

            if (gameMode !== "auto-play") {
                if (player.score >= 5) {
                    endGame('you won!');
                } else if (opponent.score >= 5) {
                    endGame('you lost :-(');
                }
            }
        }
    }

    function updateRemoteGame() {
        movePaddle(player);
        socket.send(JSON.stringify({
            'step': 'update',
            'role': player.role,
            'position': player.x
        }))
    }

    function moveAI(paddle) {
        const reactionTime = 2; // Número de frames antes de que la IA reaccione
        if (Math.random() < 1 / reactionTime) {
            // Mover hacia la pelota con un pequeño retraso
            const center = paddle.x + paddle.width / 2;
            if (center < ball.x - 10) {
                paddle.x += 4; // Velocidad de la IA
            } else if (center > ball.x + 10) {
                paddle.x -= 4;
            }
        }

        // Evitar que la paleta salga del área
        paddle.x = Math.max(0, Math.min(paddle.x, canvas.width - paddle.width));
    }

    function movePaddle(paddle) {
        if (paddle.left) {
            paddle.speed = Math.min(paddle.speed + acceleration, maxSpeed);
            paddle.x -= paddle.speed;
        } else if (paddle.right) {
            paddle.speed = Math.min(paddle.speed + acceleration, maxSpeed);
            paddle.x += paddle.speed;
        } else {
            paddle.speed = Math.max(paddle.speed - deceleration, 0);
        }

        paddle.x = Math.max(0, Math.min(paddle.x, canvas.width - paddle.width));
    }

// Listeners para el control de ambos jugadores
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') player.left = true;
        if (e.key === 'ArrowRight') player.right = true;
        if (e.key === 'a') opponent.left = true;
        if (e.key === 'd') opponent.right = true;
    });

    document.addEventListener('keyup', (e) => {
        if (e.key === 'ArrowLeft') player.left = false;
        if (e.key === 'ArrowRight') player.right = false;
        if (e.key === 'a') opponent.left = false;
        if (e.key === 'd') opponent.right = false;
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
        if (gameMode === 'auto-play') {
            drawMessage(fieldMessage);
        }
        drawDashedLine();
        drawRect(player.x, player.y, player.width, player.height, player.color);
        drawRect(opponent.x, opponent.y, opponent.width, opponent.height, opponent.color);
        drawRect(ball.x - ball.size / 2, ball.y - ball.size / 2, ball.size, ball.size, ball.color);
        drawPowerUps();
        drawScore();
        drawPlayerName();
        drawOpponentName();
    }

    /*
     * @section: Game Loops.
     *
     * @note:
     *  - gameLoop
     *  - waitingLoop
     *  - startLoop
    */
    function gameLoop() {
        if (isGameRunning) {
            if (gameMode === "auto-play") {
                moveAI(player);
                moveAI(opponent);
                moveBall();
                movePowerUps();
            } else if (gameMode !== 'remote') {
                updateGame();
            } else {
                updateRemoteGame();
            }
            drawGame();
            requestAnimationFrame(gameLoop);
        }
    }

    function waitingLoop(msg) {
        movePaddle(player);
        updateGame();
        drawMessage(msg);
        ballPlay();
        ballBounce();
        drawRect(ball.x - ball.size / 2, ball.y - ball.size / 2, ball.size, ball.size, ball.color);
        requestAnimationFrame(() => waitingLoop(msg));
    }

    function startingLoop(msg) {
        if (!isGameRunning) {
            movePaddle(player);
            drawMessage(msg);
            drawDashedLine();
            drawRect(player.x, player.y, player.width, player.height, player.color);
            drawPlayerName();
            drawOpponentName();
            requestAnimationFrame(() => startingLoop(msg));
        }
    }

    /*
     * @section: Main screen.
     *
     * Show the main screen to start the game workflow.
    */
    // menu.style.display = 'flex';
    canvasContainer.style.display = 'none';

    function autoPlay(msg) {
        gameMode = "auto-play";
        fieldMessage = msg;
        playerName = "norminette";
        opponentName = "hal-42";
        startGame();
    }

    document.addEventListener("DOMContentLoaded", function () {
        autoPlay("Click here to play!");
    });

    document.addEventListener("DOMContentLoaded", function () {
        document.getElementById("local-game").addEventListener("click", function () { setGameMode("local"); });
        document.getElementById("remote-game").addEventListener("click", function () { setGameMode("remote"); });
        document.getElementById("remote-ia-game").addEventListener("click", function () { setGameMode("remote-ai"); });
    });

}

game();

