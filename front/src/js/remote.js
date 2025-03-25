
//remote
function gameRemote()
{
	document.getElementById('content').innerHTML =
		`<canvas id="gameCanvas" width="400" height="600"></canvas>`;
	const canvas = document.getElementById("gameCanvas");
	const ctx = canvas.getContext("2d");
	const winnerMessage = document.getElementById("winnerMessage");

    // Configuración
	const paddleWidth = 80, paddleHeight = 10;
	const ballSize = 10;
	const paddleSpeed = 15;
	let ballSpeedX = 4, ballSpeedY = 4;
	const maxScore = 5; // Puntuación máxima para ganar
	let gameOver = false;
    
	// Paletas y pelota
	const player1 = { x: canvas.width / 2 - paddleWidth / 2, y: 10, score: 0 };
    const player2 = { x: canvas.width / 2 - paddleWidth / 2, y: canvas.height - 20, score: 0 };
    const ball = { x: canvas.width / 2, y: canvas.height / 2 };

	const keys = {};

	function drawRect(x, y, width, height, color) {
		ctx.fillStyle = color;
		ctx.fillRect(x, y, width, height);
	}

	function drawBall() {
		ctx.fillStyle = "white";
		ctx.beginPath();
		ctx.arc(ball.x, ball.y, ballSize / 2, 0, Math.PI * 2);
		ctx.fill();
	}

	function drawScore() {
		ctx.font = "20px Arial";
		ctx.fillText(player1.score, 20, 30);
		ctx.fillText(player2.score, 20, canvas.height - 30);
	}
	
	let player = null;
	let role = null;
	let gameStarted = false; // !!
	const socket = new WebSocket("ws://localhost:8000/ws/game/");

	/* socket.onopen = function(event) {
		const data = JSON.parse(event.data);
	} */

	socket.onmessage = function(event) {
		const data = JSON.parse(event.data);

		if (data.action === "set-player") {
			role = data.role;
			console.log('role:', role);
			if (role == "player1")
				player = player1;
			else
				player = player2;
		}
		else if (data.action === "start") {
			gameStarted = true;
			// startGame();
			gameLoop();
		}
		else if (data.action === "move") {
			if (data.player === "player1")
				player1.x = data.x;
			else
				player2.x = data.x;
		}
		else if (data.action === "ball") {
			ball.x = data.ball.x;
			ball.y = data.ball.y;
			player1.score = data.score.a;
			player2.score = data.score.b;
			drawBall();
		}
		else if (data.action === "finish") {
			socket.close();
			gameOver = true;
			gameOptions(`Player ${player1.score > player2.score ? "1" : "2"} wins!`);
			// winnerMessage.innerText = `¡Jugador ${player === player1 ? "1" : "2"} gana!`;
		}
	};
	
	document.addEventListener("keydown", (event) => keys[event.key] = true);
	document.addEventListener("keyup", (event) => keys[event.key] = false);

	function updatePaddles() {
		// if (keys["a"] && player1.x > 0) player1.x -= paddleSpeed;
		// if (keys["d"] && player1.x < canvas.width - paddleWidth) player1.x += paddleSpeed;

		if (keys["ArrowLeft"] && player.x > 0)
			player.x -= paddleSpeed;
		if (keys["ArrowRight"] && player.x < canvas.width - paddleWidth)
			player.x += paddleSpeed;
		moveData = { action: "move", player: role, x: player.x };
		if (moveData) {
			socket.send(JSON.stringify(moveData));
		}
	}

	function gameLoop() {
		if (!gameStarted) {
			ctx.fillStyle = "white";
			ctx.font = "20px Arial";
			ctx.fillText("Esperando a otro jugador...", canvas.width / 2 - 100, canvas.height / 2);
			requestAnimationFrame(gameLoop);
			return;
		}
		if (gameOver) return;
		ctx.clearRect(0, 0, canvas.width, canvas.height);

		console.log("ball: x:", ball.x, ", y:", ball.y);
		updatePaddles();
		drawRect(player1.x, player1.y, paddleWidth, paddleHeight, "white");
		drawRect(player2.x, player2.y, paddleWidth, paddleHeight, "white");
		drawBall();
		drawScore();
		// updateBall();

		requestAnimationFrame(gameLoop);
	}
}