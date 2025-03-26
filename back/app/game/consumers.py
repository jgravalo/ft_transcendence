import json
import asyncio
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer

class PongConsumer(AsyncWebsocketConsumer):
	games = {}  # Lista para almacenar jugadores
	# waiting_players = []  # Lista para almacenar jugadores
	players = [] # Lista para almacenar jugadores
	ball = {"x": 300, "y": 200, "vx": 5, "vy": 5, "width": 400, "height": 600,
		"size": 10, "max-score": 5}  # Posición y velocidad de la pelota
	
	async def find_available_room(self):
		""" Busca una sala con espacio disponible (1 jugador) """
		for room, game_list in self.games.items():
			if len(game_list) == 1:  # Si hay un solo jugador, la sala tiene espacio
				return room
		return None  # No hay salas disponibles con espacio

	async def connect(self):
		# if len(self.players) < 2:
			# username = self.scope['user'].username
			# if user.username == AnonymousUser:
			# 	username = f"Anonymous{len(self.players) + 1}"
		available_room = await self.find_available_room()

		if available_room:
			self.room_name = available_room  # Unirse a la sala con espacio
		else:
			# self.room_name = self.scope["url_route"]["kwargs"]["room_name"]  # Nueva sala
			self.room_name = f"game_{uuid.uuid4().hex[:8]}"
		
		print('set user')
		self.user = self.scope['user']
		if self.user.username == '':
				self.user.username = f"Customplayer{len(self.players) + 1}"
		print(f'user {self.user.username}: {self.user.id}')
		self.role = f"player{len(self.players) + 1}"
		self.paddle = {
			"x": 150,
			"y": 10 if len(self.players) == 0 else self.ball['height'] - 20,
			"width": 80,
			"height": 10,
			"score": 0
			}
		print('role:', self.role)
		print('paddle[y]:', self.paddle['y'])
		self.players.append(self)
		# self.waiting_players.append(self)
		
		await self.accept()
		await self.send(text_data=json.dumps({"action": "set-player", "role": self.role}))
		if len(self.players) == 2:
			print(f'user1 {self.players[0].user.username}: {self.players[0].user.id}')
			print(f'user2 {self.players[1].user.username}: {self.players[1].user.id}')
	
			print('set group')
			self.room_name = f'chat_{self.players[0].user.id}_{self.players[1].user.id}'
			self.room_group_name = f'private_{self.room_name}'
			print(f"🔗 Conectando a la sala {self.room_group_name}")
			await self.channel_layer.group_add(self.room_group_name, self.channel_name)

			# print('set game')
			# self.games[self.room_name] = []
			# self.games[self.room_name].append(self.players[0])
			# self.games[self.room_name].append(self.players[1])
			# print(f'user1: {self.games[self.room_name][0].name}')
			# print(f'user2: {self.games[self.room_name][1].name}')

			print('set ball')
			asyncio.create_task(self.start_game_loop())  # 🔥 Iniciar el bucle de la pelota

			# Cuando haya dos jugadores, avísales que pueden empezar
			for player in self.players:
				print(f'{player.role} paddle[y]:', player.paddle['y'])
				# self.players.remove(player)
				await self.channel_layer.group_add(self.room_group_name, player.channel_name)
				await player.send(text_data=json.dumps({
					"action": "start",
					"role": self.role,
					"player1": self.players[0].user.username,
					"player2": self.players[1].user.username
				}))
		# else:
		# 	await self.close()  # Si hay más de 2 jugadores, cierra la conexión

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

	async def start_game_loop(self):
		# Bucle que mueve la pelota y la sincroniza en los clientes
		while len(self.players) == 2:
			self.ball["x"] += self.ball["vx"]
			self.ball["y"] += self.ball["vy"]
			# print('ball: x:', self.ball["x"], ', y:', self.ball["y"])

			# Rebote en las paredes superior e inferior
			if self.ball["x"] <= 0 or self.ball["x"] >= self.ball["width"]:
				self.ball["vx"] *= -1  # Invertir dirección en Y

			if (self.ball["y"] <= 0 or self.ball["y"] >= self.ball["height"]):
				if self.ball["y"] <= 0:
					self.players[1].paddle["score"] += 1
				elif self.ball["y"] >= self.ball["height"]:
					self.players[0].paddle["score"] += 1
				self.ball["vy"] *= -1  # Invertir dirección en Y
				self.ball["x"] = self.ball["width"] / 2
				self.ball["y"] = self.ball["height"] / 2
				print(f'{self.players[0].paddle["score"]}-{self.players[1].paddle["score"]}')
				if (self.players[0].paddle["score"] >= self.ball["max-score"] or
					self.players[1].paddle["score"] >= self.ball["max-score"]):
					# await self.channel_layer.group_send("pong_game", {
					await self.channel_layer.group_send(self.room_group_name, {
						"type": "finish_game",
					})

			# 🏓 Verificar colisión con la paleta del jugador 1
			if (
				self.ball["y"] # - self.ball["size"] / 2
				<= self.players[0].paddle["y"] + self.players[0].paddle["height"]
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
				and self.ball["x"] >= self.players[1].paddle["x"]
				and self.ball["x"] <= self.players[1].paddle["x"] + self.players[1].paddle["width"]
			):
				print(f'choca en paleta 2: {self.ball["y"]} >= {self.players[0].paddle["y"]}')
				self.ball["vy"] *= -1
				self.ball["y"] = self.players[1].paddle["y"] - self.ball["size"]
			
			# Enviar la nueva posición de la pelota a los clientes
			await self.channel_layer.group_send(self.room_group_name, {
			# await self.channel_layer.group_send("pong_game", {
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
	
	async def finish_game(self, event):
		# Enviar la posición de la pelota a los clientes
		await self.send(text_data=json.dumps({"action": "finish"}))