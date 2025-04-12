(() => {
	let canvas, ctx;
	let player1, player2, ball;
	let paddleWidth = 10, paddleHeight = 50, ballSize = 10;
	let ballSpeedX = 5, ballSpeedY = 5;
	let paddleSpeed = 10;
	let maxScore = 5;

	let gameRunning = false;
	let gamePaused = false;
	let gameOver = false;

	let keys = {};
	let hasBouncedThisFrame = false;

	function game() {
		canvas = document.getElementById("gameCanvas");
		ctx = canvas.getContext("2d");

		player1 = { name: "Player 1", x: 10, y: canvas.height / 2 - paddleHeight / 2, score: 0 };
		player2 = { name: "Player 2", x: canvas.width - 10 - paddleWidth, y: canvas.height / 2 - paddleHeight / 2, score: 0 };
		ball = { x: canvas.width / 2, y: canvas.height / 2 };

		// --- Keydown Event Listener (also prevent scrolling) ---
		document.addEventListener("keydown", (event) => {
			if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " "].includes(event.key)) {
				event.preventDefault(); // prevent scrolling
			}
			keys[event.key] = true;
		});
		
		document.addEventListener("keyup", (event) => {
			keys[event.key] = false;
		});

		// --- Add click handlers for control buttons ---
		setupControlButtons();
	}

	function setupControlButtons() {
		// Get all control keys
		const controlKeys = document.querySelectorAll('.control-keys .key');
		
		// Add event listeners to each key
		controlKeys.forEach(key => {
			// Mouse events
			key.addEventListener('mousedown', (event) => {
				const keyText = key.textContent.trim();
				
				// Add active class for visual feedback
				key.classList.add('active');
				
				if (keyText === 'W') {
					keys['w'] = true;
				} else if (keyText === 'S') {
					keys['s'] = true;
				} else if (keyText === '↑') {
					keys['ArrowUp'] = true;
				} else if (keyText === '↓') {
					keys['ArrowDown'] = true;
				}
			});
			
			key.addEventListener('mouseup', (event) => {
				const keyText = key.textContent.trim();
				
				// Remove active class
				key.classList.remove('active');
				
				if (keyText === 'W') {
					keys['w'] = false;
				} else if (keyText === 'S') {
					keys['s'] = false;
				} else if (keyText === '↑') {
					keys['ArrowUp'] = false;
				} else if (keyText === '↓') {
					keys['ArrowDown'] = false;
				}
			});
			
			key.addEventListener('mouseleave', (event) => {
				const keyText = key.textContent.trim();
				
				// Remove active class
				key.classList.remove('active');
				
				if (keyText === 'W') {
					keys['w'] = false;
				} else if (keyText === 'S') {
					keys['s'] = false;
				} else if (keyText === '↑') {
					keys['ArrowUp'] = false;
				} else if (keyText === '↓') {
					keys['ArrowDown'] = false;
				}
			});
			
			// Touch events for mobile
			key.addEventListener('touchstart', (event) => {
				event.preventDefault(); // Prevent scrolling when touching the buttons
				const keyText = key.textContent.trim();
				
				// Add active class for visual feedback
				key.classList.add('active');
				
				if (keyText === 'W') {
					keys['w'] = true;
				} else if (keyText === 'S') {
					keys['s'] = true;
				} else if (keyText === '↑') {
					keys['ArrowUp'] = true;
				} else if (keyText === '↓') {
					keys['ArrowDown'] = true;
				}
			});
			
			key.addEventListener('touchend', (event) => {
				event.preventDefault(); // Prevent any default behavior
				const keyText = key.textContent.trim();
				
				// Remove active class
				key.classList.remove('active');
				
				if (keyText === 'W') {
					keys['w'] = false;
				} else if (keyText === 'S') {
					keys['s'] = false;
				} else if (keyText === '↑') {
					keys['ArrowUp'] = false;
				} else if (keyText === '↓') {
					keys['ArrowDown'] = false;
				}
			});
			
			key.addEventListener('touchcancel', (event) => {
				event.preventDefault(); // Prevent any default behavior
				const keyText = key.textContent.trim();
				
				// Remove active class
				key.classList.remove('active');
				
				if (keyText === 'W') {
					keys['w'] = false;
				} else if (keyText === 'S') {
					keys['s'] = false;
				} else if (keyText === '↑') {
					keys['ArrowUp'] = false;
				} else if (keyText === '↓') {
					keys['ArrowDown'] = false;
				}
			});
		});
	}

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

	function updateScoreDisplay() {
		document.getElementById("player1Score").innerText = player1.score;
		document.getElementById("player2Score").innerText = player2.score;
	}

	function updatePaddles() {
		if (keys["s"] && player1.y < canvas.height - paddleHeight) player1.y += paddleSpeed;
		if (keys["w"] && player1.y > 0) player1.y -= paddleSpeed;

		if (keys["ArrowUp"] && player2.y > 0) player2.y -= paddleSpeed;
		if (keys["ArrowDown"] && player2.y < canvas.height - paddleHeight) player2.y += paddleSpeed;
	}

	function updateBall() {
		ball.x += ballSpeedX;
		ball.y += ballSpeedY;

		if (ball.y <= 0 || ball.y >= canvas.height) {
			ballSpeedY *= -1;
		}

		function checkCollision(player) {
			if (hasBouncedThisFrame) return; // Avoid multiple collisions
			const margin = 2; // Margin of error to avoid collision issues
			if (
				ball.x + ballSize / 2 >= player.x - margin &&
				ball.x - ballSize / 2 <= player.x + paddleWidth + margin &&
				ball.y + ballSize / 2 >= player.y - margin &&
				ball.y - ballSize / 2 <= player.y + paddleHeight + margin
			) {
				if (ball.x < canvas.width / 2) {
					ball.x = player.x + paddleWidth + ballSize / 2 + 1;
				} else {
					ball.x = player.x - ballSize / 2 - 1;
				}
				let hitPosition = (ball.y - player.y) / paddleHeight - 0.5;
				ballSpeedY = hitPosition * 6;
				ballSpeedX *= -1;

				hasBouncedThisFrame = true;
			}
		}

		checkCollision(player1);
		checkCollision(player2);

		if (ball.x <= 0) {
			player2.score++;
			checkWin(player2);
			resetBall();
		}
		else if (ball.x >= canvas.width) {
			player1.score++;
			checkWin(player1);
			resetBall();
		}

		updateScoreDisplay();
	}

	function resetBall() {
		if (gameOver) return;
		ball.x = canvas.width / 2;
		ball.y = canvas.height / 2;
		ballSpeedX *= -1;
	}

	function checkWin(player) {
		if (player.score >= maxScore) {
			gameOver = true;
			finishGame(player);
			gameRunning = false;
		}
	}

	function finishGame(player) {
		ctx.fillText(player.name + " wins!", canvas.width / 2, canvas.height / 2);
		document.getElementById('startGame').classList.remove('disabled');
	}

	function resetGame() {
		player1.score = 0;
		player2.score = 0;
		player1.y = canvas.height / 2 - paddleHeight / 2;
		player2.y = canvas.height / 2 - paddleHeight / 2;
		ball.x = canvas.width / 2;
		ball.y = canvas.height / 2;
		gameOver = false;
		gamePaused = false;
		updateScoreDisplay();
	}

	function gameLoop() {
		if (!gameRunning || gamePaused) return;
		hasBouncedThisFrame = false; // Reset the flag for the next frame
		ctx.clearRect(0, 0, canvas.width, canvas.height);
		updatePaddles();
		drawRect(player1.x, player1.y, paddleWidth, paddleHeight, "white");
		drawRect(player2.x, player2.y, paddleWidth, paddleHeight, "white");
		drawBall();
		updateBall();

		requestAnimationFrame(gameLoop);
	}

	function showCountdown() {
		let countdown = ["Ready", "3", "2", "1", "Go!"];
		let countIndex = 0;
		ctx.clearRect(0, 0, canvas.width, canvas.height);
		ctx.font = "30px Arial";
		ctx.fillStyle = "white";
		ctx.textAlign = "center";

		function nextCount() {
			ctx.clearRect(0, 0, canvas.width, canvas.height);
			ctx.fillText(countdown[countIndex], canvas.width / 2, canvas.height / 2);
			countIndex++;
			if (countIndex < countdown.length) {
				setTimeout(nextCount, 800);
			} else {
				gameRunning = true;
				gamePaused = false;
				requestAnimationFrame(gameLoop);
			}
		}
		nextCount();
	}

	window.setupLocalGame = function (){
		const startBtn = document.getElementById('startGame');
		const pauseBtn = document.getElementById('pauseGame');
		if (!startBtn || !pauseBtn) {
			console.error('startBtn or pauseBtn not found');
			return;
		}

		startBtn.addEventListener('click', () => {
			startBtn.classList.add('disabled');
			resetGame()
			showCountdown();
		});

		pauseBtn.addEventListener('click', () => {
			if (gameRunning && !gameOver) {
				gamePaused = !gamePaused;
				pauseBtn.setAttribute("data-i18n", gamePaused ? "game.resume" : "game.pause");
				changeLanguage(localStorage.getItem("selectedLanguage") || "en"); // Update the texts based on the language
				requestAnimationFrame(gameLoop);
			}
		});
		// Initialize game once	
		game();
	}
})();