let gameSocket = null;
let room = '';
/* 
let winner = null;
//remote
function gameRemote(url)
{
	const params = new URLSearchParams(new URL(url).search);
	let route = `ws://${base.slice(7)}/ws/game/`;
	if (params.get("user"))
		route += `?user=${params.get("user")}&token=${sessionStorage.getItem('access')}`
	else if (params.get("room"))
	{
		console.log(`params.get("room") = ${params.get("room")}`);
		route += `?room=${params.get("room")}`
		if (params.get("tournament"))
			route += `&round=${params.get("round")}&tournament=${params.get("tournament")}`
		route += `&token=${sessionStorage.getItem('access')}`
	}
	else
		route += `?token=${sessionStorage.getItem('access')}`;
	console.log(`route = ${route}`);
	gameSocket = new WebSocket(route);
		const canvas = document.getElementById("gameCanvas");
		const ctx = canvas.getContext("2d");
		const winnerMessage = document.getElementById("winnerMessage");
*/

(() => {
	let canvas, ctx;
	let paddleWidth = 10, paddleHeight = 50, ballSize = 10;
	let paddleSpeed = 10;

	let player1, player2, ball;
	let keys = {};
	let role = null;
	let player = null;

	let gameRunning = false;
	let gameOver = false;

	// --- Setup and Initialization ---
	function gameRemote(url) {
		console.log('🚀 Initializing remote game with URL:', url);
		canvas = document.getElementById("gameCanvas");
		ctx = canvas.getContext("2d");

		player1 = { name: "Player 1", x: 0, y: 0, score: 0 };
		player2 = { name: "Player 2", x: 0, y: 0, score: 0 };
		ball = { x: 0, y: 0 };

		setupWebSocket(url);

		// --- Setup control buttons ---
		setupControlButtons();
	}

	function setupControlButtons() {

		// --- Control keys in the UI ---
		const controlKeys = document.querySelectorAll('.control-keys .key');
		const keyMap = { '↑': 'ArrowUp', '↓': 'ArrowDown' };
	
		function setKey(keyText, state) {
			const key = keyMap[keyText];
			if (key) keys[key] = state;
		}
	
		controlKeys.forEach(key => {
			const keyText = key.textContent.trim();
	
			// Mouse events
			key.addEventListener('mousedown', () => {
				key.classList.add('active');
				setKey(keyText, true);
			});
			key.addEventListener('mouseup', () => {
				key.classList.remove('active');
				setKey(keyText, false);
			});
	
			// Touch events
			key.addEventListener('touchstart', (e) => {
				e.preventDefault();
				key.classList.add('active');
				setKey(keyText, true);
			});
			key.addEventListener('touchend', (e) => {
				e.preventDefault();
				key.classList.remove('active');
				setKey(keyText, false);
			});
		});

		// --- Keydown Control Key (also prevent scrolling) ---
		document.addEventListener("keydown", (event) => {
			if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " "].includes(event.key)) {
				event.preventDefault(); // prevent scrolling
			}
			keys[event.key] = true;
		});
		
		document.addEventListener("keyup", (event) => {
			keys[event.key] = false;
		});
	}

	// --- WebSocket Setup ---
	function setupWebSocket(url) {
		const params = new URLSearchParams(new URL(url).search);
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		let hostname = window.location.host;
		// let hostname = window.location.hostname;
		// if (hostname === 'localhost') hostname += ':8080';

		let route = `${protocol}//${hostname}/ws/game/`;
		if (params.get("user")) {
			route += `?user=${params.get("user")}&token=${sessionStorage.getItem('access')}`;
		} else if (params.get("room")) {
			route += `?room=${params.get("room")}`;
			if (params.get("tournament"))
				route += `&round=${params.get("round")}&tournament=${params.get("tournament")}`;
			route += `&token=${sessionStorage.getItem('access')}`;
		} else {
			route += `?token=${sessionStorage.getItem('access')}`;
		}
		console.log('🌐 WebSocket URL:', route);

		gameSocket = new WebSocket(route);

		gameSocket.onopen = () => console.log("WebSocket connected");
		gameSocket.onclose = () => { gameOver = true; console.log("WebSocket closed"); };

		gameSocket.onmessage = (event) => {
			const data = JSON.parse(event.data);
			handleServerMessage(data);
		};
	}

	// --- Handle WebSocket Messages ---
	function handleServerMessage(data) {
		console.log('📩 Message from server:', data);
		switch (data.action) {
			case "set-player":
				role = data.role;
				player = (role === "player1") ? player1 : player2;
				break;

			case "start":
				player1.y = player2.y = canvas.height / 2 - paddleHeight / 2;
				player1.x = 10;
				player2.x = canvas.width - paddleWidth - 10;
				ball.x = canvas.width / 2;
				ball.y = canvas.height / 2;
				player1.name = data.player1;
				player2.name = data.player2;
				updateNamesRemote();
				gameRunning = true;
				updateStatusMessage('game.status.progress');
				requestAnimationFrame(gameLoop);
				break;

			case "move":
				if (data.player === "player1") player1.y = data.y;
				else player2.y = data.y;
				break;

			case "ball":
				ball.x = data.ball.x;
				ball.y = data.ball.y;
				player1.score = data.score.a;
				player2.score = data.score.b;
				updateScoreDisplayRemote();
				break;

			case "finish":
			case "disconnect":
				// document.getElementById('content').innerText = `${data.winner} has won`;
				finishGame(data.winner);
				break;
		}
	}

	// --- Drawing Functions ---
	function drawRect(x, y, width, height, color = "white") {
		ctx.fillStyle = color;
		ctx.fillRect(x, y, width, height);
	}

	function drawBall() {
		ctx.fillStyle = "white";
		ctx.beginPath();
		ctx.arc(ball.x, ball.y, ballSize / 2, 0, Math.PI * 2);
		ctx.fill();
	}

	function updateScoreDisplayRemote() {
		document.getElementById("player1Score").innerText = player1.score;
		document.getElementById("player2Score").innerText = player2.score;
	}

	function updateNamesRemote() {
		document.getElementById("player1Name").innerText = player1.name;
		document.getElementById("player2Name").innerText = player2.name;
	}

	// --- Paddle Controls ---
	function updatePaddlesRemote() {
		if (keys["ArrowUp"] && player.y > 0)
			player.y -= paddleSpeed;
		if (keys["ArrowDown"] && player.y < canvas.height - paddleHeight)
			player.y += paddleSpeed;
		gameSocket.send(JSON.stringify({ action: "move", player: role, y: player.y }));
	}

	// --- Game Loop ---
	function gameLoop() {
		if (!gameRunning || gameOver) return;

		ctx.clearRect(0, 0, canvas.width, canvas.height);
		updatePaddlesRemote();
		drawRect(player1.x, player1.y, paddleWidth, paddleHeight);
		drawRect(player2.x, player2.y, paddleWidth, paddleHeight);
		drawBall();
		requestAnimationFrame(gameLoop);
	}

	function finishGame(winner) {
		gameRunning = false;
		gameOver = true;
		document.getElementById('startGame').classList.remove('disabled');
		
		// Add debugging to see what's being compared
		console.log("Game finished. Winner:", winner);
		console.log("Current player:", player.name);
		console.log("Player 1:", player1.name);
		console.log("Player 2:", player2.name);
		
		if (winner === player1.name && role === "player1" || winner === player2.name && role === "player2") {
			updateStatusMessage('game.status.win');
		} else {
			updateStatusMessage('game.status.lose');
		}
	}
	
	function resetRemoteGame() {
		player1.score = 0;
		player2.score = 0;
		player1.y = canvas.height / 2 - paddleHeight / 2;
		player2.y = canvas.height / 2 - paddleHeight / 2;
		ball.x = canvas.width / 2;
		ball.y = canvas.height / 2;
		gameOver = false;
		updateScoreDisplayRemote(); // Reset score DOM elements
		ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear canvas visuals
	}

	function updateStatusMessage(messageKey) {
		document.getElementById('statusMessage').setAttribute('data-i18n', messageKey);
		changeLanguage(localStorage.getItem("selectedLanguage") || "en");
	}

	// --- Game Setup ---
	window.setupRemoteGame = function() {
		const startBtn = document.getElementById('startGame');
		if (!startBtn) {
			console.error('startBtn not found');
			return;
		}

		startBtn.addEventListener('click', () => {
			if (gameOver) {
				resetRemoteGame();
			}
			const wsUrl = `${window.location.origin}/game/remote/${room}`; //{{ link|escapejs }}';
			console.log('🌐 Creating WebSocket with URL:', wsUrl);
			
			updateStatusMessage('game.status.matchmaking');

			gameRemote(wsUrl);
			startBtn.classList.add('disabled');
		});
	}
})();