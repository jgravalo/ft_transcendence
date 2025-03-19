
function game()
{
	const canvas = document.getElementById("gameCanvas");
	const ctx = canvas.getContext("2d");

	// Configuración del juego
	const paddleWidth = 10, paddleHeight = 80;
	const ballSize = 10;
	const paddleSpeed = 5;
	let ballSpeedX = 4, ballSpeedY = 4;

	// Paletas y pelota
	const player1 = { x: 10, y: canvas.height / 2 - paddleHeight / 2, score: 0 };
	const player2 = { x: canvas.width - 20, y: canvas.height / 2 - paddleHeight / 2, score: 0 };
	const ball = { x: canvas.width / 2, y: canvas.height / 2 };

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
		ctx.fillText(player1.score, canvas.width / 4, 30);
		ctx.fillText(player2.score, (canvas.width / 4) * 3, 30);
	}
	
	// ball
	function updateBall() {
		ball.x += ballSpeedX;
		ball.y += ballSpeedY;
	
		// Rebote en paredes superior e inferior
		if (ball.y <= 0 || ball.y >= canvas.height) {
			ballSpeedY *= -1;
		}
	
		// Rebote en paletas
		if (
			(ball.x <= player1.x + paddleWidth && ball.y >= player1.y && ball.y <= player1.y + paddleHeight) ||
			(ball.x >= player2.x - ballSize && ball.y >= player2.y && ball.y <= player2.y + paddleHeight)
		) {
			ballSpeedX *= -1;
		}
	
		// Punto para un jugador
		if (ball.x <= 0) {
			player2.score++;
			resetBall();
		} else if (ball.x >= canvas.width) {
			player1.score++;
			resetBall();
		}
	}
	
	function resetBall() {
		ball.x = canvas.width / 2;
		ball.y = canvas.height / 2;
		ballSpeedX *= -1;
	}

	// keys
	document.addEventListener("keydown", function (event) {
		if (event.key === "w" && player1.y > 0) player1.y -= paddleSpeed;
		if (event.key === "s" && player1.y < canvas.height - paddleHeight) player1.y += paddleSpeed;
	
		if (event.key === "ArrowUp" && player2.y > 0) player2.y -= paddleSpeed;
		if (event.key === "ArrowDown" && player2.y < canvas.height - paddleHeight) player2.y += paddleSpeed;
	});
	
	// loop
	function gameLoop() {
		ctx.clearRect(0, 0, canvas.width, canvas.height);
	
		// Dibujar elementos
		drawRect(0, 0, canvas.width, canvas.height, "black");
		drawRect(player1.x, player1.y, paddleWidth, paddleHeight, "white");
		drawRect(player2.x, player2.y, paddleWidth, paddleHeight, "white");
		drawBall();
		drawScore();
	
		// Actualizar posición de la pelota
		updateBall();
	
		requestAnimationFrame(gameLoop);
	}
	
	gameLoop();
	
}

game();