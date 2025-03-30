
function game() {
    // document.getElementById("get-challenges").addEventListener("click", getChallenges);
    let message = null;
    let gameInstance = null;

    const socket_game = new WebSocket('ws://localhost:8080/ws/game/');
	console.log('init socket');

    class PongGame {
        constructor(mode = "auto-play", extra = null) {
            // --- Game Mode and status
            if (mode === "remote_challenge" || mode === "challenge_created" || mode === "user-challenged") {
                this.mode = "remote";
            } else {
                this.mode = mode;
            }
            this.running = true;
            this.waiting = false;
            this.listening = false;
            this.id = null;
            // --- Canvas
            this.canvas = document.getElementById('pongCanvas');
			this.ctx = this.canvas.getContext('2d');
			if (this.ctx) {
				console.log("Canvas soportado");
			} else {
				console.log("Canvas no soportado en este navegador");
			}			
            this.canvas.width = 400;
            this.canvas.height = 800;
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            // --- Vars
            this.countdownInterval = null
            this.paddleWidth = 100
            this.paddleHeight = 15;
            this.minPaddleWidth = 45;
            this.maxPaddleWidth = this.canvas.width - 45;
            this.acceleration = 2;
            this.deceleration = 1;
            this.maxSpeed = 20;
            this.collisionCount = 0;
            this.score1 = 0;
            this.score2 = 0;
            if (this.mode !== "auto-play") {
                message = null;
                this.playerName = "player1";
                this.opponentName = "player2";
            } else {
                this.playerName = "Norminette";
                this.opponentName = "Hal42";
            }
            // --- Remote Vars
            this.socket = socket_game;
            this.player = {
                playerName: this.playerName,
                role: 'player1',
                left: false,
                right: false,
                x: this.canvas.width / 2 - this.paddleWidth / 2,
                y: this.canvas.height - 80,
                width: this.paddleWidth,
                height: this.paddleHeight,
                color: '#4ac1f7',
                powerUp: null,
                score: 0,
                points: 0,
                speed: 0,
                speedModifier: 1
            };

            this.opponent = {
                playerName: this.opponentName,
                role: 'player2',
                left: false,
                right: false,
                x: this.canvas.width / 2 - this.paddleWidth / 2,
                y: 60,
                width: this.paddleWidth,
                height: this.paddleHeight,
                color: '#fff',
                powerUp: null,
                score: 0,
                points: 0,
                speed: 0,
                speedModifier: 1
            };

            this.ball = {
                x: this.canvas.width / 2,
                y: this.canvas.height / 2,
                size: 15,
                speedX: 4,
                speedY: 4,
                baseSpeed: 4,
                color: '#fff'
            };

            this.base_ball = {
                speedX: 4,
                speedY: 4,
                baseSpeed: 4,
            };
            // --- Power Ups
            this.powerUps = [];
            this.powerUpSize = this.ball.size * 1.5;
            this.collisionCount = 0;
            this.collisionThreshold = 5;
            this.activationDistance = this.powerUpSize * 3;
            this.powerUpColors = {
                '>>': 'green',
                '<<': 'red'
            };
            this.initEventListeners();
            this.initUIListeners();
            this.initCanvasListeners("auto-play", "overlay");
            this.initCanvasListeners("remote", "cancel-wait");
            if (this.mode === "remote-ai" || this.mode === "remote") {
                this.listening = true;
                if (mode === "remote_challenge" || mode === "user-challenged") return;
                if (mode === "challenge_created") {
                    this.socket.send(JSON.stringify({
                        step: 'create_challenge'
                    }))
                } else {
                    this.socket.send(JSON.stringify({
                            step: 'join',
                            username: this.playerName,
                            player: this.player,
                            mode: this.mode
                        }
                    ));
                }
            }
            if (this.mode !== "menu") {
                this.gameLoop();
            }
        }

        destroy(reset=true) {
            this.running = false;
            this.listening = false;
            document.removeEventListener('keydown', this.keydownHandler);
            document.removeEventListener('keyup', this.keyUpHandler);
            this.canvas.removeEventListener("click", this.canvasClickHandler);
            document.removeEventListener("click", this.documentClickHandler);

            if (this.socket && !reset) {
                this.socket.send(JSON.stringify({
                    'step': 'end',
                    'mode': this.mode,
                    'score1': this.player["score"],
                    'score2': this.opponent["score"]
                }))
            }
        }

        // -- Game Loop
        gameLoop(lastTime = 0) {
            if (!this.running) return;

            const now = performance.now();
            const deltaTime = now - lastTime;

            if (deltaTime >= (1000 / 60)) {
                if (this.mode) {
                    if (this.mode === "auto-play") {
                        this.moveAI(this.player);
                        this.moveAI(this.opponent);
                        this.moveBall();
                        this.movePowerUps();
                    } else {
                        this.updateGame();
                    }
                    this.drawGame();
                }

                lastTime = now;
            }

            requestAnimationFrame(() => this.gameLoop(lastTime));
        }

        updateRemoteGame() {
            if (!this.running) return;
            if (this.mode === "remote") {
                this.movePaddle(this.player);
                this.socket.send(JSON.stringify({
                    'step': 'update',
                    'role': this.player.role,
                    'position': this.player.x
                }))
            } else {
                this.socket.send(JSON.stringify({
                    'step': 'move',
                    'opponent': this.opponent,
                    'ball': this.ball
                }))
            }
        }

        updateGame() {
            if (!this.mode) return;
            // TODO CHECK THIS BEHAVIOUR
            if (this.running && !this.waiting && (this.mode === "remote" || this.mode === "remote-ai")) {
                this.updateRemoteGame();
                if (this.mode === "remote") return;
            }
            this.movePaddle(this.player);
            this.movePaddle(this.opponent);
            this.moveBall();
            this.movePowerUps();
            this.checkPowerUpCollisions();

            if (this.mode !== "auto-play") {
                if (this.player.score >= 5) {
                    if (this.mode === "local") {
                        this.endGame("Player1 Won!");
                    }
                    this.endGame('you won!');
                } else if (this.opponent.score >= 5) {
                    if (this.mode === "local") {
                        this.endGame("Player2 Won!");
                    }
                    this.endGame('you lost :-(');
                }
            }
        }

        drawGame() {
            this.drawRect(0, 0, this.canvas.width, this.canvas.height, '#000');
            if (message !== null) {
                this.drawMessage(message);
            }
            this.drawDashedLine();

            this.drawRect(this.player.x, this.player.y, this.player.width, this.player.height, this.player.color);
            this.drawRect(this.opponent.x, this.opponent.y, this.opponent.width, this.opponent.height, this.opponent.color);
            this.drawRect(this.ball.x - this.ball.size / 2, this.ball.y - this.ball.size / 2, this.ball.size, this.ball.size, this.ball.color);
            this.drawPowerUps();
            this.drawScore();
            this.drawPlayerName();
            this.drawOpponentName();
        }

        game_listener(data) {
            if (!this.listening) {
                if (data.step !== 'close') return;
            }
            if (data.step === 'error') {
                message = "Error at game";
                this.clickMode(message, "auto-play", "remote-match");
            } else if (data.step === 'wait') {
                this.running = false;
                this.waiting = true;
                this.resetBall();
                this.playerName = data.playerName;
                this.waitingLoop('Waiting for a victim!');
            } else if (data.step === 'ready') {
                this.waiting = false;
                this.running = false;
                if (data.playerRole === 'player1') {
                    Object.assign(this.player, data.player1);
                    this.playerName = data.playerName;
                    this.opponentName = data.opponentName;
                } else {
                    Object.assign(this.player, data.player2);
                    this.playerName = data.opponentName;
                    this.opponentName = data.playerName;
                }
                this.startingLoop(data.message);
            } else if (data.step === 'start') {
                console.log(data.id);
                this.id = data.id;
                this.waiting = false;
                this.running = true;
                this.opponentName = data.opponentName;
                this.playerName = data.playerName;
                this.gameLoop();
            } else if (data.step === 'go') {
                console.log(data.id);
                this.waiting = false;
                this.running = true;
                this.id = data.id;
                this.playerName = data.player1Name;
                this.opponentName = data.player2Name;
                if (this.player.role === 'player1') {
                    Object.assign(this.opponent, data.player2);
                    Object.assign(this.player, data.player1);
                } else {
                    Object.assign(this.opponent, data.player1);
                    Object.assign(this.player, data.player2);
                }
                Object.assign(this.ball, data.ball);
                this.updateRemoteGame();
                this.gameLoop();
            } else if (data.step === 'endOfGame') {
                this.listening = false;
                this.running = false;
                this.openMenu("remote-match");
                this.startCountdown(10, "rematch-countdown", () => {
                    this.clickMode(message, "auto-play", "remote-match");
                });
            } else if (data.step === "end") {
                this.clickMode(message, "auto-play", "remote-match")
            } else if (data.step === 'move') {
                this.opponent.x = data.position;
            } else if (data.step === 'update') {
                Object.assign(this.opponent, data.opponent);
                Object.assign(this.player, data.player);
                Object.assign(this.ball, data.ball);
                this.score1 = data.score1;
                this.score2 = data.score2;
                this.powerUps = data.powerUps;
            }
        }

        // -- Remote Mode loops
        waitingLoop(msg) {
            if (!this.waiting) return;
            this.movePaddle(this.player);
            this.drawMessage(msg);
            this.ballPlay();
            this.ballBounce();
            this.drawRect(this.ball.x - this.ball.size / 2, this.ball.y - this.ball.size / 2, this.ball.size, this.ball.size, this.ball.color);
            requestAnimationFrame(() => this.waitingLoop(msg));

        }

        startingLoop(msg) {
            if (!this.running && !this.waiting) {
                this.movePaddle(this.player);
                this.drawMessage(msg);
                this.drawDashedLine();
                this.drawRect(this.player.x, this.player.y, this.player.width, this.player.height, this.player.color);
                this.drawPlayerName();
                this.drawOpponentName();
                requestAnimationFrame(() => this.startingLoop(msg));
            }
        }

        // -- Rematch countdown
        startCountdown(seconds, elementId, callback) {
            let counter = seconds;
            const countdownElement = document.getElementById(elementId);
            if (this.countdownInterval) {
                clearInterval(this.countdownInterval);
            }
            countdownElement.innerText = counter;
            this.countdownInterval = setInterval(() => {
                counter--;
                countdownElement.innerText = counter;

                if (counter <= 0) {
                    clearInterval(this.countdownInterval);
                    this.countdownInterval = null;
                    if (typeof callback === "function") {
                        callback();
                    }
                }
            }, 1000);
        }

        // -- Listeners
        initEventListeners() {
            this.keydownHandler = (e) => {
                if (e.key === 'ArrowLeft') this.player.left = true;
                if (e.key === 'ArrowRight') this.player.right = true;
                if (this.mode === 'local') {
                    if (e.key === 'a') this.opponent.left = true;
                    if (e.key === 'd') this.opponent.right = true;
                }
            };
            this.keyUpHandler = (e) => {
                if (e.key === 'ArrowLeft') this.player.left = false;
                if (e.key === 'ArrowRight') this.player.right = false;
                if (this.mode === 'local') {
                    if (e.key === 'a') this.opponent.left = false;
                    if (e.key === 'd') this.opponent.right = false;
                }
            };
            document.addEventListener('keydown', this.keydownHandler);
            document.addEventListener('keyup', this.keyUpHandler);
        }

        rematch(mode) {
            if (mode === 'join') {
                this.waiting = true;
                this.running = false;
                this.listening = true;
                this.waitingLoop('Waiting for a rematch!');
                this.socket.send(JSON.stringify({
                    'step': 'rematch'
                }))
            } else {
                this.socket.send(JSON.stringify({
                    'step': 'rematch-cancel',
                    'id': this.id
                }))
            }
        }

        abort_waiting() {
            this.waiting = false;
            this.listening = false;
            this.socket.send(JSON.stringify({
                    'step': 'abort-waiting'
                }))
            this.clickMode("Click here to play!", "auto-play", "cancel-wait");
        }

        clickMode(msg, mode, element = "overlay", reset=true) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null
            this.closeMenu(element);
            this.endGame(msg, mode, reset);
        }

        initUIListeners() {
            this.uiHandlers = {
                local: () => this.clickMode(null, "local"),
                remote: () => this.clickMode(null, "remote"),
                remoteAI: () => this.clickMode(null, "remote-ai"),
                create_challenge: () => this.clickMode(null, "challenge_created"),
                rematch_ok: () => this.rematch('join'),
                rematch_cancel: () => this.rematch('cancel'),
                waiting_cancel: () => this.abort_waiting()
            };

            document.getElementById("local-game").addEventListener("click", this.uiHandlers.local);
            document.getElementById("remote-game").addEventListener("click", this.uiHandlers.remote);
            document.getElementById("remote-challenge").addEventListener("click", this.uiHandlers.create_challenge);
            document.getElementById("remote-ia-game").addEventListener("click", this.uiHandlers.remoteAI);
            document.getElementById("accept-rematch").addEventListener("click", this.uiHandlers.rematch_ok);
            document.getElementById("reject-rematch").addEventListener("click", this.uiHandlers.rematch_cancel);
            document.getElementById("end-waiting").addEventListener("click", this.uiHandlers.waiting_cancel);
        }

        openMenu(element) {
            const menu = document.getElementById(element);
            const canvas = this.canvas.getBoundingClientRect();

            menu.style.width = `${canvas.width}px`;
            menu.style.height = `${canvas.height}px`;
            menu.style.top = `${canvas.top}px`;
            menu.style.left = `${canvas.left}px`;
            menu.style.display = "flex";
        }

        closeMenu(element) {
            if (!element) return;
            const menu = document.getElementById(element);
            menu.style.display = "none";
        }

        initCanvasListeners(condition, element) {
            this.canvasClickHandler = (event) => {
                if (this.mode === condition) {
                    this.openMenu(element);
                }
            };

            this.documentClickHandler = (event) => {
                const menu = document.getElementById(element);
                if (menu.style.display === "flex" && !this.canvas.contains(event.target) && !menu.contains(event.target)) {
                    menu.style.display = "none";
                }
            };

            this.canvas.addEventListener("click", this.canvasClickHandler);
            document.addEventListener("click", this.documentClickHandler);
        }

        // -- Game Control
        moveAI(paddle) {
            const reactionTime = 2;
            if (Math.random() < 1 / reactionTime) {
                const center = paddle.x + paddle.width / 2;
                if (center < this.ball.x - 10) {
                    paddle.x += 4;
                } else if (center > this.ball.x + 10) {
                    paddle.x -= 4;
                }
            }
            paddle.x = Math.max(0, Math.min(paddle.x, this.canvas.width - paddle.width));
        }

        movePaddle(paddle) {
            if (paddle.left) {
                paddle.speed = Math.min(paddle.speed + this.acceleration, this.maxSpeed);
                paddle.x -= paddle.speed;
            } else if (paddle.right) {
                paddle.speed = Math.min(paddle.speed + this.acceleration, this.maxSpeed);
                paddle.x += paddle.speed;
            } else {
                paddle.speed = Math.max(paddle.speed - this.deceleration, 0);
            }
            paddle.x = Math.max(0, Math.min(paddle.x, this.canvas.width - paddle.width));
        }

        // -- Ball Functions
        moveBall() {
            this.ballPlay();
            if (this.ball.y - this.ball.size / 2 <= 0) {
                this.player.score++;
                this.resetBall();
            } else if (this.ball.y + this.ball.size / 2 >= this.canvas.height) {
                this.opponent.score++;
                this.resetBall();
            }

            if (this.checkCollision(this.player)) {
                this.ball.y = this.player.y - this.ball.size / 2;
                this.ball.speedY = -Math.abs(this.ball.baseSpeed * this.player.speedModifier);
            } else if (this.checkCollision(this.opponent)) {
                this.ball.y = this.opponent.y + this.opponent.height + this.ball.size / 2;
                this.ball.speedY = Math.abs(this.ball.baseSpeed * this.opponent.speedModifier);
            }
            this.generatePowerUp();
        }

        ballPlay() {
            this.ball.x += this.ball.speedX;
            this.ball.y += this.ball.speedY;

            if (this.ball.x - this.ball.size / 2 <= 0) {
                this.ball.x = this.ball.size / 2;
                this.ball.speedX = Math.abs(this.ball.baseSpeed * this.player.speedModifier);
                this.collisionCount++;
            }
            if (this.ball.x + this.ball.size / 2 >= this.canvas.width) {
                this.ball.x = this.canvas.width - this.ball.size / 2;
                this.ball.speedX = -Math.abs(this.ball.baseSpeed * this.opponent.speedModifier);
                this.collisionCount++;
            }
        }

        ballBounce() {
            if (this.ball.y - this.ball.size <= 0) {
                this.ball.y = this.ball.size;
                this.ball.speedY = Math.abs(this.ball.baseSpeed);
            } else if (this.ball.y + this.ball.size >= this.canvas.height) {
                this.ball.y = this.canvas.height - this.ball.size;
                this.ball.speedY = -Math.abs(this.ball.baseSpeed);
            }
        }

        resetBall() {
            Object.assign(this.ball, this.base_ball);
            this.ball.x = this.canvas.width / 2;
            this.ball.y = this.canvas.height / 2;
            const angle = (Math.random() - 0.5) * Math.PI / 8;
            this.ball.speedX = this.ball.baseSpeed * Math.sin(angle);
            this.ball.speedY = this.ball.baseSpeed * Math.cos(angle) * (Math.random() > 0.5 ? 1 : -1);
            this.collisionCount = 0;
        }

        checkCollision(paddle) {
            const collision =
                this.ball.x > paddle.x &&
                this.ball.x < paddle.x + paddle.width &&
                this.ball.y + this.ball.size / 2 > paddle.y &&
                this.ball.y - this.ball.size / 2 < paddle.y + paddle.height;

            if (collision) {
                const hitPoint = this.ball.x - (paddle.x + paddle.width / 2);
                const normalizedHitPoint = hitPoint / (paddle.width / 2);
                this.ball.speedX = normalizedHitPoint * 6;
            }

            return collision;
        }

        // --- Power Ups
        movePowerUps() {
            for (let i = this.powerUps.length - 1; i >= 0; i--) {
                const powerUp = this.powerUps[i];
                powerUp.y += powerUp.speedY;
                powerUp.x += powerUp.speedX;

                if (powerUp.x + this.powerUpSize > this.canvas.width || powerUp.x < 0) {
                    powerUp.speedX = -powerUp.speedX;
                }

                if (powerUp.y > this.canvas.height || powerUp.y < 0) {
                    this.powerUps.splice(i, 1);
                }
            }
        }

        generatePowerUp() {
            if (this.collisionCount >= this.collisionThreshold && this.powerUps.length === 0) {
                const fromPlayer = Math.random() > 0.5;
                const paddle = fromPlayer ? this.player : this.opponent;
                const directionY = fromPlayer ? -3 : 3;
                const directionX = (Math.random() - 0.5) * 2;
                const types = ['>>', '<<']; // Lista inicial de power-ups
                const type = types[Math.floor(Math.random() * types.length)];
                this.powerUps.push({
                    x: paddle.x + paddle.width / 2 - this.powerUpSize / 2,
                    y: paddle.y,
                    startY: paddle.y,
                    speedY: directionY,
                    speedX: directionX,
                    type,
                    active: false
                });
                this.collisionCount = 0;
            }
        }

        applyPowerUp(player, powerUpType) {
            if (powerUpType === '>>') {
                player.width = Math.min(player.width + 10, this.maxPaddleWidth);
                player.speedModifier = Math.max(player.speedModifier - 0.1, 0.8);
                player.powerUp = '>>';
            } else if (powerUpType === '<<') {
                player.width = Math.max(player.width - 10, this.minPaddleWidth);
                player.speedModifier = Math.min(player.speedModifier + 0.1, 1.2);
                player.powerUp = '<<';
            }
        }

        checkPowerUpCollisions() {
            for (let i = this.powerUps.length - 1; i >= 0; i--) {
                const powerUp = this.powerUps[i];
                const distance = Math.abs(powerUp.startY - powerUp.y);
                powerUp.active = distance >= this.activationDistance;

                if (!powerUp.active) continue;

                if (
                    this.ball.x < powerUp.x + this.powerUpSize &&
                    this.ball.x + this.ball.size > powerUp.x &&
                    this.ball.y < powerUp.y + this.powerUpSize &&
                    this.ball.y + this.ball.size > powerUp.y
                ) {
                    this.ball.speedY = -this.ball.speedY;
                    this.ball.speedX = -this.ball.speedX;
                    this.powerUps.splice(i, 1);
                    continue;
                }

                if (
                    powerUp.x < this.player.x + this.player.width &&
                    powerUp.x + this.powerUpSize > this.player.x &&
                    powerUp.y < this.player.y + this.player.height &&
                    powerUp.y + this.powerUpSize > this.player.y
                ) {
                    this.applyPowerUp(this.player, powerUp.type);
                    this.powerUps.splice(i, 1);
                } else if (
                    powerUp.x < this.opponent.x + this.opponent.width &&
                    powerUp.x + this.powerUpSize > this.opponent.x &&
                    powerUp.y < this.opponent.y + this.opponent.height &&
                    powerUp.y + this.powerUpSize > this.opponent.y
                ) {
                    this.applyPowerUp(this.opponent, powerUp.type);
                    this.powerUps.splice(i, 1);
                }
            }
        }

        drawRect(x, y, width, height, color) {
            this.ctx.fillStyle = color;
            this.ctx.fillRect(x, y, width, height);
        }

        drawDashedLine() {
            this.ctx.strokeStyle = "#fff";
            this.ctx.setLineDash([15, 15]);
            this.ctx.lineWidth = 15;
            this.ctx.beginPath();
            this.ctx.moveTo(0, this.canvas.height / 2);
            this.ctx.lineTo(this.canvas.width, this.canvas.height / 2);
            this.ctx.stroke();
            this.ctx.setLineDash([]);
        }

        drawPlayerName() {
            this.ctx.font = "40px Silkscreen";
            this.ctx.fillStyle = "#fff";
            this.ctx.textAlign = "left";
            this.ctx.fillText(this.playerName, 0, this.canvas.height - 5);
        }

        drawOpponentName() {
            this.ctx.font = "40px Silkscreen";
            this.ctx.fillStyle = "#fff";
            this.ctx.textAlign = "right";
            this.ctx.fillText(this.opponentName, this.canvas.width, 35);
        }

        drawMessage(announce) {
            this.drawRect(0, 0, this.canvas.width, this.canvas.height, '#000');
            this.ctx.font = "30px Silkscreen";
            this.ctx.fillStyle = "#fff";
            this.ctx.textAlign = "center";
            this.ctx.fillText(announce, this.canvas.width / 2, this.canvas.height / 2 + 70, this.canvas.width - 10);
        }

        drawScore() {
            this.ctx.font = "70px Silkscreen";
            this.ctx.fillStyle = "#fff";
            this.ctx.textAlign = "right";
            if (this.mode === 'remote') {
                this.ctx.fillText(this.score1, this.canvas.width - 20, this.canvas.height / 2 + 140);
                this.ctx.fillText(this.score2, this.canvas.width - 20, this.canvas.height / 2 - 100);
            } else {
                this.ctx.fillText(this.player.score, this.canvas.width - 20, this.canvas.height / 2 + 140);
                this.ctx.fillText(this.opponent.score, this.canvas.width - 20, this.canvas.height / 2 - 100);
            }

        }

        drawPowerUps() {
            for (const powerUp of this.powerUps) {
                this.ctx.fillStyle = this.powerUpColors[powerUp.type];
                this.ctx.font = '20px Silkscreen';
                this.ctx.textAlign = 'center';
                this.ctx.fillText(powerUp.type, powerUp.x + this.powerUpSize / 2, powerUp.y + this.powerUpSize / 1.5);
                this.drawRect(powerUp.x, powerUp.y, this.powerUpSize, this.powerUpSize, this.powerUpColors[powerUp.type]);
            }
        }

        endGame(msg, mode = "auto-play", reset=true) {
            message = msg;
            this.running = false;
            startNewGame(mode);
        }
    }

    function startNewGame(mode) {
        if (gameInstance) {
            gameInstance.destroy();
        }
        if (mode === "auto-play") {
            gameInstance = new PongGame("auto-play");
        } else {
            gameInstance = new PongGame(mode);
        }
    }

    function renderChallenges(element, data, accept, reject, challenge_user, accept_step="accept_challenge", reject_step="reject_challenge") {
      const container = document.getElementById(element);
      container.innerHTML = "";

        if (!Array.isArray(data)) {
            return;
        }

      data.forEach((challenge) => {
        const li = document.createElement("li");
        const textNode = document.createTextNode(challenge.username);
        li.appendChild(textNode);
        const iconsDiv = document.createElement("div");
        if (accept) {
            const acceptSpan = document.createElement("span");
            acceptSpan.classList.add("material-symbols-outlined");
            acceptSpan.textContent = "play_arrow";
            acceptSpan.title = "Accept";
            acceptSpan.addEventListener("click", (event) => {
              event.stopPropagation();
              gameInstance.clickMode(null, "remote_challenge", null, false);
              socket_game.send(JSON.stringify({
                step: accept_step,
                challenge_id: challenge.id
              }));
            });
            iconsDiv.appendChild(acceptSpan);
        }
        if (reject) {
            const rejectSpan = document.createElement("span");
            rejectSpan.classList.add("material-symbols-outlined");
            rejectSpan.textContent = "close";
            rejectSpan.title = "Reject";
            rejectSpan.addEventListener("click", (event) => {
                event.stopPropagation();
                socket_game.send(JSON.stringify({
                    step: "reject_challenge",
                    challenge_id: challenge.id
                }));
            });
            iconsDiv.appendChild(rejectSpan);
        }
        if (challenge_user) {
            const challengeSpan = document.createElement("span");
            challengeSpan.classList.add("material-symbols-outlined");
            challengeSpan.textContent = "target";
            challengeSpan.title = "Challenge";
            challengeSpan.addEventListener("click", (event) => {
                // TODO: improve to avoid error
                gameInstance.clickMode(null, "user-challenged", null, false);
                event.stopPropagation();
                socket_game.send(JSON.stringify({
                    step: "challenge-user",
                    challenge_id: challenge.id
                }));
            });
            iconsDiv.appendChild(challengeSpan);
        }
        li.appendChild(iconsDiv);
        container.appendChild(li);
      });
    }

    function append_message(message) {
        const container = document.getElementById("game-log-tab");
        const li = document.createElement("li");
        const textNode = document.createTextNode(message);
        li.appendChild(textNode);
        container.appendChild(li);
        li.scrollIntoView({ behavior: "smooth", block: "end" });
    }

    function socket_listener() {
        socket_game.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (gameInstance && ("step" in data)) {
                gameInstance.game_listener(data);
            } else {
                if (data.payload_update === "challenges-update") {
                    renderChallenges("random-challenges-tab", data.detail, true, false, false, "accept_challenge", "reject_challenge");
                } else if (data.payload_update === "my-challenges") {
                    renderChallenges("my-challenges-tab", data.detail, true, true, false, "accept_my_challenge", "reject_my_challenge");
                    const myChallengeButton = document.getElementById('my-challenges');
                    myChallengeButton.click();
                } else if (data.payload_update === "connected-users") {
                    renderChallenges("connected-users-tab", data.detail, false, false, true);
                } else if (data.payload_update === "log-update") {
                    append_message(data.detail);
                } else if (data.payload_update === "game-abort") {
                   append_message(data.detail);
                   this.clickMode(message, "auto-play", "remote-match");
                   socket_game.send(JSON.stringify({
                          step: "game-cancel"
                   }));
                }
            }
        };
    }
    // --- GENERAL MANAGEMENT

    document.addEventListener("DOMContentLoaded", manageGame);

	function manageGame() {
		console.log("in manageGame");
        const tabButtons = document.querySelectorAll('.tab-button');

        tabButtons.forEach(button => {
          button.addEventListener('click', () => {
            const targetTabId = button.getAttribute('data-tab');
            document.querySelectorAll('.tab-data').forEach(tabSection => {
              tabSection.style.display = 'none';
            });

            const targetTab = document.getElementById(targetTabId);
            if (targetTab) {
              targetTab.style.display = 'block';
            }
          });
        });

        message = "Click here to play!";
        if (socket_game !== null) {
            socket_game.onopen = () => {
                socket_game.send(JSON.stringify({
                        step: 'handshake'
                    }
                ));
            }
        }
        gameInstance = new PongGame('auto-play');
        socket_listener();
    }
	
	manageGame();
	// );
}

// game();
