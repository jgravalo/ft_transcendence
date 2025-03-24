import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class PongConsumer(AsyncWebsocketConsumer):
	players = []  # Lista para almacenar jugadores
	ball = {"x": 300, "y": 200, "vx": 5, "vy": 5, "width": 400, "height": 600, "size": 10}  # Posición y velocidad de la pelota

	async def connect(self):
		if len(self.players) < 2:
			# username = self.scope['user'].username
			# if user.username == AnonymousUser:
			# 	username = f"Anonymous{len(self.players) + 1}"
			self.name = self.scope['user'].username
			self.role = f"player{len(self.players) + 1}"
			# self.paddle['y'] = 10 if len(self.players) == 0 else self.ball['height'] - 20
			self.paddle = {
				"x": 150,
				"y": 10 if len(self.players) == 0 else self.ball['height'] - 20,
				"width": 80,
				"height": 10,
				"score": 0
				}
			# self.role = "player1" if len(self.players) == 0 else "player2"
			print('role:', self.role)
			print('paddle[y]:', self.paddle['y'])
			self.players.append(self)
			
			await self.accept()
			await self.send(text_data=json.dumps({"action": "set-player", "role": self.role}))

			if len(self.players) == 2:
				await self.channel_layer.group_add("pong_game", self.channel_name)
				print("🚀 Dos jugadores conectados. Iniciando el juego...")
				asyncio.create_task(self.start_game_loop())  # 🔥 Iniciar el bucle de la pelota
				
				# Cuando haya dos jugadores, avísales que pueden empezar
				for player in self.players:
					print(f'{player.role} paddle[y]:', player.paddle['y'])
					await self.channel_layer.group_add("pong_game", player.channel_name)
					await player.send(text_data=json.dumps({"action": "start", "role": self.role}))
		else:
			await self.close()  # Si hay más de 2 jugadores, cierra la conexión

	async def disconnect(self, close_code):
		if self in self.players:
			print(f'{self.role} has been disconnected')
			self.players.remove(self)

	async def receive(self, text_data):
		data = json.loads(text_data)
		self.paddle['x'] = data['x']
		# print(f'{self.role} paddle[x]:', self.paddle['x'])
		# role = data['role']
		# print('text_data: ', text_data)
		# Reenvía los datos al otro jugador
		for player in self.players:
			if player != self:
				await player.send(text_data=json.dumps(data))

	""" 	async def check_collision(self, player):
		if (
			self.ball["y"] + self.ball["size"] >= player.paddle['y'] and
			self.ball["y"] <= player.paddle['y'] + player.paddle["height"] and
			self.ball["y"] >= player.paddle['x'] and
			self.ball["y"] <= player.paddle['x'] + player.paddle["width"]
		):
			hitPosition = (self.ball['x'] - self.paddle['x'])
			self.ball["vx"] *= hitPosition * 6  # Ajusta la dirección X según el punto de impacto
			self.ball["vy"] *= -1  # Invertir dirección en Y """

	"""
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
			"""

	async def check_collision(self):
		print('esta en check_collision')
		if (
			self.ball["y"] + self.ball["size"] >= self.players[0].paddle['y'] and
			self.ball["y"] <= self.players[0].paddle['y'] + self.players[0].paddle["height"] and
			self.ball["y"] >= self.players[0].paddle['x'] and
			self.ball["y"] <= self.players[0].paddle['x'] + self.players[0].paddle["width"]
		):
			hitPosition = (self.ball['x'] - self.players[0].paddle['x'])
			self.ball["vx"] *= hitPosition * 6  # Ajusta la dirección X según el punto de impacto
			self.ball["vy"] *= -1  # Invertir dirección en Y
			print("🎾 La bola ha rebotado en la paleta de arriba")
		if (
			self.ball["y"] + self.ball["size"] >= self.players[1].paddle['y'] and
			self.ball["y"] <= self.players[1].paddle['y'] + self.players[1].paddle["height"] and
			self.ball["y"] >= self.players[1].paddle['x'] and
			self.ball["y"] <= self.players[1].paddle['x'] + self.players[1].paddle["width"]
		):
			hitPosition = (self.ball['x'] - self.players[1].paddle['x'])
			self.ball["vx"] *= hitPosition * 6  # Ajusta la dirección X según el punto de impacto
			self.ball["vy"] *= -1  # Invertir dirección en Y
			print("🎾 La bola ha rebotado en la paleta de abajo")
	
	async def check_paddle_collision(self):
		"""Detecta si la pelota toca una paleta y ajusta la dirección"""
		ball_x, ball_y = self.ball["x"], self.ball["y"]

		# Paleta izquierda (player1)
		if ball_x <= self.paddle[1]["x"] + self.paddle[1]["width"]:  
			if self.paddle[1]["y"] <= ball_y <= self.paddle[1]["y"] + self.paddle[1]["height"]:
				self.ball["vx"] *= -1  # Cambia la dirección horizontal
				self.ball["x"] = self.paddle[1]["x"] + self.paddle[1]["width"]  # Evita bug de superposición
				print("🎾 La bola ha rebotado en la paleta izquierda")

		# Paleta derecha (player2)
		if ball_x >= self.paddle[2]["x"] - self.paddle[2]["width"]:
			if self.paddle[2]["y"] <= ball_y <= self.paddle[2]["y"] + self.paddle[2]["height"]:
				self.ball["vx"] *= -1
				self.ball["x"] = self.paddle[2]["x"] - self.paddle[2]["width"]
				print("🎾 La bola ha rebotado en la paleta derecha")

	async def start_game_loop(self):
		# Bucle que mueve la pelota y la sincroniza en los clientes
		while len(self.players) == 2:
			self.ball["x"] += self.ball["vx"]
			self.ball["y"] += self.ball["vy"]
			# print('ball: x:', self.ball["x"], ', y:', self.ball["y"])

			# Rebote en las paredes superior e inferior
			if self.ball["x"] <= 0 or self.ball["x"] >= self.ball["width"]:
				self.ball["vx"] *= -1  # Invertir dirección en Y

			""" if self.ball["y"] <= 0 or self.ball["y"] >= self.ball["height"]:
				self.ball["vy"] *= -1  # Invertir dirección en Y """
			"""
			if (
				(ball.y <= player1.y + paddleHeight &&
				ball.x >= player1.x &&
				ball.x <= player1.x + paddleWidth) ||
				(ball.y >= player2.y - ballSize &&
				ball.x >= player2.x &&
				ball.x <= player2.x + paddleWidth)
				)
			{
				ballSpeedY *= -1;
			}
			"""
			"""
			if (
				self.ball["y"] + self.ball["size"] >= self.paddle['y'] and
				self.ball["y"] <= self.paddle['y'] + self.paddle["height"] and
				self.ball["y"] >= self.paddle['x'] and
				self.ball["y"] <= self.paddle['x'] + self.paddle["width"]
			):
				hitPosition = (self.ball['x'] - self.paddle['x'])
				self.ball["vx"] *= hitPosition * 6  # Ajusta la dirección X según el punto de impacto
				self.ball["vy"] *= -1  # Invertir dirección en Y
			"""
			# print('paddle[0][y]:', self.players[0].paddle['y'], 'paddle[1][y]:', self.players[1].paddle['y'])
			# self.check_collision(self.players[0])
			# self.check_collision(self.players[1])
			# self.check_collision()
			# self.check_paddle_collision()

			if (
				self.ball["y"] <= 0 or
				self.ball["y"] >= self.ball["height"]
				):
				if self.ball["y"] <= 0:
					self.players[0].paddle["score"] += 1
				elif self.ball["y"] >= self.ball["height"]:
					self.players[1].paddle["score"] += 1
				self.ball["vy"] *= -1  # Invertir dirección en Y
				self.ball["x"] = self.ball["width"] / 2
				self.ball["y"] = self.ball["height"] / 2
				print(f'{self.players[0].paddle["score"]}-{self.players[1].paddle["score"]}')
			
			# if self.ball["y"] <= self.players[0].paddle["height"] * 2:
			# 	self.ball["vy"] *= -1  # Invertir dirección en Y
			# elif self.ball["y"] >= self.ball["height"] - self.players[0].paddle["height"] * 2:
			# 	self.ball["vy"] *= -1  # Invertir dirección en Y
			
			# 🏓 Verificar colisión con la paleta del jugador 1
			if (
				self.ball["y"] # - self.ball["size"] / 2
				<= self.players[0].paddle["y"] + self.players[0].paddle["height"]
				# <= 10 + 10 = 20
				and self.ball["x"] >= self.players[0].paddle["x"]
				and self.ball["x"] <= self.players[0].paddle["x"] + self.players[0].paddle["width"]
			):
				print(f'choca en paleta 1: {self.ball["y"]} <= {self.players[0].paddle["y"]} + {self.players[0].paddle["height"]}')
				self.ball["vy"] *= -1  # Invierte la dirección vertical
				self.ball["y"] = self.players[0].paddle["y"] + self.players[0].paddle["height"] # Evita quedarse pegada
			# 🏓 Verificar colisión con la paleta del jugador 2
			elif (
				self.ball["y"] # + self.ball["size"] / 2
				>= self.players[1].paddle["y"]
				# >= 580 
				and self.ball["x"] >= self.players[1].paddle["x"]
				and self.ball["x"] <= self.players[1].paddle["x"] + self.players[1].paddle["width"]
			):
				print(f'choca en paleta 2: {self.ball["y"]} + {self.ball["size"]} >= {self.players[0].paddle["y"]}')
				self.ball["vy"] *= -1
				self.ball["y"] = self.players[1].paddle["y"] - self.ball["size"]
			
			# Enviar la nueva posición de la pelota a los clientes
			await self.channel_layer.group_send("pong_game", {
					"type": "ball_update",
					"ball": self.ball,
					"score": {
						"a": self.players[0].paddle["score"],
						"b": self.players[1].paddle["score"]
					}
				}
			)
			await asyncio.sleep(0.03)  # Controla la velocidad de actualización

	async def ball_update(self, event):
		# Enviar la posición de la pelota a los clientes
		await self.send(text_data=json.dumps({"action": "ball", "ball": event["ball"], "score": event["score"]}))
