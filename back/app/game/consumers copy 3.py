import json
import asyncio
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer

class PongConsumer(AsyncWebsocketConsumer):
	# players = []  # Lista para almacenar jugadores
	ball = {"x": 300, "y": 200, "vx": 5, "vy": 5, "width": 400, "height": 600,
		"size": 10, "max-score": 2}  # Posición y velocidad de la pelota
	players = {}  # Diccionario para almacenar jugadores en cada sala

	async def find_available_room(self):
		""" Busca una sala con espacio disponible (1 jugador) """
		for room, player_list in self.players.items():
			if len(player_list) == 1:  # Si hay un solo jugador, la sala tiene espacio
				return room
		return None  # No hay salas disponibles con espacio

	async def connect(self):
		# Buscar una sala con espacio
		available_room = await self.find_available_room()

		if available_room:
			self.room_name = available_room  # Unirse a la sala con espacio
		else:
			# self.room_name = self.scope["url_route"]["kwargs"]["room_name"]  # Nueva sala
			self.room_name = f"game_{uuid.uuid4().hex[:8]}"

		# Agregar jugador a la sala
		if self.room_name not in self.players:
			self.players[self.room_name] = []

		# Asignar datos
		self.user = self.scope['user']
		self.name = self.user.username if self.user.is_authenticated else f"Customplayer{len(self.players[self.room_name]) + 1}"
		print(f'user \'{self.name}\': \'{self.user.id}\'')
		self.role = f"player{len(self.players[self.room_name]) + 1}"
		self.paddle = {
			"x": 150,
			"y": 10 if len(self.players[self.room_name]) == 0 else self.ball['height'] - 20,
			"width": 80,
			"height": 10,
			"score": 0
		}
		player_data = {
			"channel_name": self.channel_name,
			"user": self.user,
			"name": self.name,
			"role": self.role,
			"paddle": self.paddle
		}

		# Unirse a la sala
		self.room_group_name = f"pong_{self.room_name}"
		await self.channel_layer.group_add(self.room_group_name, self.channel_name)
		await self.accept()
		await self.send(text_data=json.dumps({"action": "set-player", "role": self.role}))
		self.players[self.room_name].append(player_data)

		# Verificar si la sala está completa
		if len(self.players[self.room_name]) == 2:
			asyncio.create_task(self.start_game_loop())  # 🔥 Iniciar el bucle de la pelota
			await self.channel_layer.group_send(self.room_group_name,{
				"type": "start_game",
				"action": "start",
				"player1": self.players[self.room_name][0]["name"],
				"player2": self.players[self.room_name][1]["name"]
				})
		# else:
		# 	await self.send(json.dumps({"type": "waiting", "message": "Esperando a otro jugador..."}))

	async def disconnect(self, close_code):

		await self.channel_layer.group_send(self.room_group_name, {
			"type": "finish_game",
			"winner": winner,
		})
		if self in self.players[self.room_name]:
			print(f'{self.role} has been disconnected')
			self.players[self.room_name].remove(self)

	async def receive(self, text_data):
		data = json.loads(text_data)
		self.paddle['x'] = data['x']
		# print(f'{self.role} paddle[x]:', self.paddle['x'])
		# role = data['role']
		# print('text_data: ', text_data)
		# Reenvía los datos al otro jugador
		# for player in self.players[self.room_name]:
		# 	if player["channel_name"] != self.channel_name:
		# 		await self.channel_layer.send(player["channel_name"], text_data=json.dumps(data))
		print(self.room_name)  # Verifica que la sala esté bien asignada
		print(self.players)  # Verifica que self.players tenga la estructura correcta
		for player in self.players[self.room_name]:
			if player["channel_name"] != self.channel_name:  # Asegurarnos de no enviar el mensaje al jugador actual
				await self.channel_layer.send(player["channel_name"], {
					"type": "websocket.send",  # Clave estándar para enviar mensaje de WebSocket
					"text": json.dumps(data)   # Usar "text" para el mensaje
				})
				# await player.send(text_data=json.dumps(data))

	async def start_game_loop(self):
		# Bucle que mueve la pelota y la sincroniza en los clientes
		self.players = self.players[self.room_name]
		# player1 = self.players[0]
		# player2 = self.players[1]
		while len(self.players) == 2:
			# Si un jugador se desconecta, detenemos el bucle
			if not all(p["channel_name"] in self.channel_layer.channels for p in self.players[self.room_name]):
				print("Un jugador se desconectó. Terminando el juego.")
				break
			self.ball["x"] += self.ball["vx"]
			self.ball["y"] += self.ball["vy"]
			# print('ball: x:', self.ball["x"], ', y:', self.ball["y"])

			# Rebote en las paredes superior e inferior
			if self.ball["x"] <= 0 or self.ball["x"] >= self.ball["width"]:
				self.ball["vx"] *= -1  # Invertir dirección en Y

			if (self.ball["y"] <= 0 or self.ball["y"] >= self.ball["height"]):
				if self.ball["y"] <= 0:
					self.players[1]["paddle"]["score"] += 1
				elif self.ball["y"] >= self.ball["height"]:
					self.players[0]["paddle"]["score"] += 1
				self.ball["vy"] *= -1  # Invertir dirección en Y
				self.ball["x"] = self.ball["width"] / 2
				self.ball["y"] = self.ball["height"] / 2
				print(f'{self.players[0]["paddle"]["score"]}-{self.players[1]["paddle"]["score"]}')
				if (self.players[0]["paddle"]["score"] >= self.ball["max-score"] or
					self.players[1]["paddle"]["score"] >= self.ball["max-score"]):
					# await self.channel_layer.group_send("pong_game", {
					if self.players[0]["paddle"]["score"] >= self.ball["max-score"]:
						winner =  self.players[0]["name"]
					elif self.players[1]["paddle"]["score"] >= self.ball["max-score"]:
						winner =  self.players[1]["name"]
					await self.channel_layer.group_send(self.room_group_name, {
						"type": "finish_game",
						"winner": winner,
					})

			# 🏓 Verificar colisión con la paleta del jugador 1
			if (
				self.ball["y"] # - self.ball["size"] / 2
				<= self.players[0]["paddle"]["y"] + self.players[0]["paddle"]["height"]
				and self.ball["x"] >= self.players[0]["paddle"]["x"]
				and self.ball["x"] <= self.players[0]["paddle"]["x"] + self.players[0]["paddle"]["width"]
			):
				print(f'choca en paleta 1: {self.ball["y"]} <= {self.players[0]["paddle"]["y"]} + {self.players[0]["paddle"]["height"]}')
				self.ball["vy"] *= -1  # Invierte la dirección vertical
				self.ball["y"] = self.players[0]["paddle"]["y"] + self.players[0]["paddle"]["height"] # Evita quedarse pegada
			# 🏓 Verificar colisión con la paleta del jugador 2
			elif (
				self.ball["y"] # + self.ball["size"] / 2
				>= self.players[1]["paddle"]["y"]
				and self.ball["x"] >= self.players[1]["paddle"]["x"]
				and self.ball["x"] <= self.players[1]["paddle"]["x"] + self.players[1]["paddle"]["width"]
			):
				print(f'choca en paleta 2: {self.ball["y"]} >= {self.players[0].paddle["y"]}')
				self.ball["vy"] *= -1
				self.ball["y"] = self.players[1]["paddle"]["y"] - self.ball["size"]
			
			# Enviar la nueva posición de la pelota a los clientes
			await self.channel_layer.group_send(self.room_group_name, {
			# await self.channel_layer.group_send("pong_game", {
					"type": "ball_update",
					"ball": self.ball,
					"score": {
						"a": self.players[0]["paddle"]["score"],
						"b": self.players[1]["paddle"]["score"]
					}
				}
			)
			await asyncio.sleep(0.03)  # Controla la velocidad de actualización

	async def start_game(self, event):
		# Enviar la posición de la pelota a los clientes
		await self.send(text_data=json.dumps({"action": "start",
			"player1": event["player1"], "player2": event["player2"]}))

	async def ball_update(self, event):
		# Enviar la posición de la pelota a los clientes
		await self.send(text_data=json.dumps({"action": "ball", "ball": event["ball"], "score": event["score"]}))
	
	async def finish_game(self, event):
		# Enviar la posición de la pelota a los clientes
		await self.send(text_data=json.dumps({"action": "finish", "winner": event["winner"]}))
