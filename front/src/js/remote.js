let gameSocket = null;
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

	
	let player = null;
	let winner = null;
	let role = null;
	let gameStarted = false; // !!
	gameSocket = new WebSocket('ws://' + base.slice(7, -5) + ':8080/ws/game/');

	gameSocket.onopen = function(event) {
		console.log(`socket opened`);
	}

	gameSocket.onmessage = function(event) {
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
			console.log('data.player1:', data.player1);
			console.log('data.player2:', data.player2);
			player1.name = data.player1;
			player2.name = data.player2;
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
		else if (data.action === "finish" || data.action === "disconnect") {
			// console.log(`disconnection ${player.name}`);
			// if (data.action === "finish")
				// gameSocket.close();
			console.log(`action ${data.action}`);
			gameOver = true;
			winner = data.winner;
			// winnerMessage.innerText = `¡Jugador ${player === player1 ? "1" : "2"} gana!`;
		}
	};
	
	gameSocket.onclose = function(event) {
		gameOver = true;
		console.log(`socket closed`);
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
			gameSocket.send(JSON.stringify(moveData));
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
		if (gameOver)
		{
			console.log("pathname = ", window.location.pathname);
			if (window.location.pathname == '/game')
				gameOptions(`${winner} wins!`);
			return ;
		}
		ctx.clearRect(0, 0, canvas.width, canvas.height);

		// console.log("ball: x:", ball.x, ", y:", ball.y);
		updatePaddles();
		drawRect(player1.x, player1.y, paddleWidth, paddleHeight, "white");
		drawRect(player2.x, player2.y, paddleWidth, paddleHeight, "white");
		drawBall();
		drawPlayers();
		drawScore();

		requestAnimationFrame(gameLoop);
	}
}