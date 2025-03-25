
function gameOptions(winner = "")
{
	// <h2 id="winnerMessage">${winner}</h2>
	document.getElementById('content').innerHTML = `
	<h2 id="winnerMessage"></h2>
	<button onclick="game()">LOCAL</button>
	<button onclick="gameRemote()">REMOTE</button>
	`;
	document.getElementById('winnerMessage').innerText = winner;
}

function game()
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
	const player1 = { x: canvas.width / 2 - paddleWidth / 2, y: 10,
		name: 'player1', score: 0 };
    const player2 = { x: canvas.width / 2 - paddleWidth / 2, y: canvas.height - 20,
		name: 'player2', score: 0 };
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
	
	function drawPlayers() {
		ctx.font = "20px Arial";
		ctx.fillText(player1.name, 20, 30);
		ctx.fillText(player2.name, 20, canvas.height - 30);
	}

	function drawScore() {
		ctx.font = "20px Arial";
		ctx.fillText(player1.score, canvas.width - 20, 30);
		ctx.fillText(player2.score, canvas.width - 20, canvas.height - 30);
	}

	function updateBall() {
		ball.x += ballSpeedX;
		ball.y += ballSpeedY;

		// Rebote en los lados
		if (ball.x <= 1 || ball.x >= canvas.width - 1) {
			ballSpeedX *= -1;
		}
		

		// Rebote en paletas con mejor detección de colisión
		function checkCollision(player) {
			if (
				ball.y + ballSize >= player.y &&
				ball.y <= player.y + paddleHeight &&
				ball.x >= player.x &&
				ball.x <= player.x + paddleWidth
			)
			{
				let hitPosition = (ball.x - player.x) / paddleWidth - 0.5; // Rango de -0.5 a 0.5
				ballSpeedX = hitPosition * 6; // Ajusta la dirección X según el punto de impacto
				ballSpeedY *= -1;
			}
		}
		checkCollision(player1);
		checkCollision(player2);

		// Punto para un jugador
		if (gameOver)
			return;
		if (ball.y <= 0) {
			player2.score++;
			checkWin(player2);
			resetBall();
		}
		else if (ball.y >= canvas.height) {
			player1.score++;
			checkWin(player1);
			resetBall();
		}
	}

	function checkWin(player) {
		if (player.score >= maxScore) {
			gameOver = true;
			// winnerMessage.innerText = `¡Jugador ${player === player1 ? "1" : "2"} gana!`;
		}
	}

	function resetBall() {
		if (gameOver) return;
		ball.x = canvas.width / 2;
		ball.y = canvas.height / 2;
		ballSpeedY *= -1;
	}

	document.addEventListener("keydown", (event) => keys[event.key] = true);
	document.addEventListener("keyup", (event) => keys[event.key] = false);

	function updatePaddles() {
		if (keys["a"] && player1.x > 0) player1.x -= paddleSpeed;
		if (keys["d"] && player1.x < canvas.width - paddleWidth) player1.x += paddleSpeed;

		if (keys["ArrowLeft"] && player2.x > 0) player2.x -= paddleSpeed;
		if (keys["ArrowRight"] && player2.x < canvas.width - paddleWidth) player2.x += paddleSpeed;
	}

	function gameLoop() {
		if (gameOver)
		{
			// winnerMessage.innerText = `¡Jugador ${player === player1 ? "1" : "2"} gana!`;
			gameOptions(`Player ${player1.score > player2.score ? "1" : "2"} wins!`);
			return;
		}
		ctx.clearRect(0, 0, canvas.width, canvas.height);

		updatePaddles();
		drawRect(player1.x, player1.y, paddleWidth, paddleHeight, "white");
		drawRect(player2.x, player2.y, paddleWidth, paddleHeight, "white");
		drawBall();
		drawPlayers();
		drawScore();
		updateBall();

		requestAnimationFrame(gameLoop);
	}
	gameLoop();

}
