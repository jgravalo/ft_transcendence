import json
import asyncio
import uuid
from asgiref.sync import sync_to_async
from django.apps import apps
from channels.generic.websocket import AsyncWebsocketConsumer

class PongConsumer(AsyncWebsocketConsumer):
	games = {}  # Lista para almacenar jugadores
	ball = {}  # Lista para almacenar jugadores
	
	async def find_available_room(self):
		""" Busca una sala con espacio disponible (1 jugador) """
		print('in find_available_room')
		print(f'len games = {len(self.games)}')
		for room, game_list in self.games.items():
			print(f'room {room}; len1: {len(game_list)}; len2: {len(self.games[room])}')
			if len(game_list) == 1:  # Si hay un solo jugador, la sala tiene espacio
				return room
		return None  # No hay salas disponibles con espacio

	async def connect(self):
		# Obtener la sala desde la URL o algún identificador
		""" 
		self.room_name = self.scope["url_route"]["kwargs"].get("user2")
		self.room_name = self.scope["url_route"]["kwargs"].get("room_name")
		if not self.room_name:  # Si no se proporciona una sala, crea una nueva
			self.room_name = f"game_{uuid.uuid4().hex[:8]}"
		if self.room_name not in self.games:
			self.games[self.room_name] = []  # Nueva sala
		"""
		"""
        self.user2 = self.scope['url_route']['kwargs']['other_user_id']  # Para hacer el otro usuario
		if self.user2:
		"""
		available_room = await self.find_available_room()
		print('set game')
		if available_room:
			self.room_name = available_room  # Unirse a la sala con espacio
			print('room available')
		else:
			# self.room_name = self.scope["url_route"]["kwargs"]["room_name"]  # Nueva sala
			self.room_name = f"game_{uuid.uuid4().hex[:8]}"
			self.games[self.room_name] = []
			print('new room')
		
		print(f'room_name in connect = {self.room_name}')
		self.room_group_name = f'private_{self.room_name}'
		print('set user')
		self.user = self.scope['user']
		self.name = self.user.username if self.user.is_authenticated else f"Customplayer{len(self.games[self.room_name]) + 1}"
		# print(f'user {self.name}: {self.user.id}')
		self.role = f"player{len(self.games[self.room_name]) + 1}"
		self.paddle = {
			"x": 150,
			"y": 10 if len(self.games[self.room_name]) == 0 else 580,
			"width": 80,
			"height": 10,
			"score": 0
			}
		print('role:', self.role)
		print('paddle[y]:', self.paddle['y'])
		print(f'user: {self.name} {self}')
		self.games[self.room_name].append(self)
		
		await self.accept()
		await self.send(text_data=json.dumps({"action": "set-player", "role": self.role}))
		if len(self.games[self.room_name]) == 2:
			print('set group')
			print(f"🔗 Conectando a la sala {self.room_group_name}")
			# await self.channel_layer.group_add(self.room_group_name, self.channel_name)
			print('set ball')
			self.ball[self.room_name] = {"x": 300, "y": 200, "vx": 5, "vy": 5,
				"width": 400, "height": 600, "size": 10, "max-score": 3, "connect": True}

			asyncio.create_task(self.start_game_loop())  # 🔥 Iniciar el bucle de la pelota

			# Cuando haya dos jugadores, avísales que pueden empezar
			for player in self.games[self.room_name]:
				print(f'{player.role} paddle[y]:', player.paddle['y'])
				await self.channel_layer.group_add(self.room_group_name, player.channel_name)
				await player.send(text_data=json.dumps({
					"action": "start",
					"role": self.role,
					"player1": self.games[self.room_name][0].name,
					"player2": self.games[self.room_name][1].name
				}))

	async def disconnect(self, close_code):
		print(f'room_name in disconnect = {self.room_name}')
		self.ball[self.room_name]['connect'] = False
		if self in self.games[self.room_name]:
			for player in self.games[self.room_name]:
				if self != player:
					await player.send(text_data=json.dumps({
						"action": "finish",
						"winner": player.name
					}))
				await player.close()
				await self.channel_layer.group_discard(self.room_group_name, player.channel_name)
			print(f'{self.role} has been disconnected in games')
			# self.games[self.room_name].remove(self)
			# await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
			self.games[self.room_name].clear()

	async def receive(self, text_data):
		# print(f'room_name in receive = {self.room_name}')
		data = json.loads(text_data)
		self.paddle['x'] = data['x']
		for player in self.games[self.room_name]:
			if player != self:
				await player.send(text_data=json.dumps(data))

	async def start_game_loop(self):
		ball = self.ball[self.room_name]
		print(f'room_name in ball = {self.room_name}')
		# Bucle que mueve la pelota y la sincroniza en los clientes
		while len(self.games[self.room_name]) == 2:
			ball["x"] += ball["vx"]
			ball["y"] += ball["vy"]
			# print('ball: x:', self.ball["x"], ', y:', self.ball["y"])

			# Rebote en las paredes superior e inferior
			if ball["x"] <= 0 or ball["x"] >= ball["width"]:
				ball["vx"] *= -1  # Invertir dirección en Y

			if (ball["y"] <= 0 or ball["y"] >= ball["height"]):
				if ball["y"] <= 0:
					self.games[self.room_name][1].paddle["score"] += 1
				elif ball["y"] >= ball["height"]:
					self.games[self.room_name][0].paddle["score"] += 1

				ball["vy"] *= -1  # Invertir dirección en Y
				ball["x"] = ball["width"] / 2
				ball["y"] = ball["height"] / 2
				print(f'{self.games[self.room_name][0].paddle["score"]}-{self.games[self.room_name][1].paddle["score"]}')

				if (self.games[self.room_name][0].paddle["score"] >= ball["max-score"] or
					self.games[self.room_name][1].paddle["score"] >= ball["max-score"]):
					if self.games[self.room_name][0].paddle["score"] >= ball["max-score"]:
						winner =  self.games[self.room_name][0].name
					elif self.games[self.room_name][1].paddle["score"] >= ball["max-score"]:
						winner =  self.games[self.room_name][1].name
					if (self.games[self.room_name][0].user.is_authenticated and
					self.games[self.room_name][1].user.is_authenticated):
						Match = apps.get_model('game', 'Match')
						game = await sync_to_async(Match.objects.create)(
							player1=self.games[self.room_name][0].user,
							player2=self.games[self.room_name][1].user,
							score_player1=self.games[self.room_name][0].paddle["score"],
							score_player2=self.games[self.room_name][1].paddle["score"],
						)
					await self.channel_layer.group_send(self.room_group_name, {
						"type": "finish_game",
						"winner": winner
					})
					self.close()
					break
			if not self.ball[self.room_name]['connect']:
				self.close()
				break

			# 🏓 Verificar colisión con la paleta del jugador 1
			if (
				ball["y"] # - self.ball["size"] / 2
				<= self.games[self.room_name][0].paddle["y"] + self.games[self.room_name][0].paddle["height"]
				and ball["x"] >= self.games[self.room_name][0].paddle["x"]
				and ball["x"] <= self.games[self.room_name][0].paddle["x"] + self.games[self.room_name][0].paddle["width"]
			):
				print(f'choca en paleta 1: {ball["y"]} <= {self.games[self.room_name][0].paddle["y"]} + {self.games[self.room_name][0].paddle["height"]}')
				ball["vy"] *= -1  # Invierte la dirección vertical
				ball["y"] = self.games[self.room_name][0].paddle["y"] + self.games[self.room_name][0].paddle["height"] # Evita quedarse pegada
			# 🏓 Verificar colisión con la paleta del jugador 2
			elif (
				ball["y"] # + self.ball["size"] / 2
				>= self.games[self.room_name][1].paddle["y"]
				and ball["x"] >= self.games[self.room_name][1].paddle["x"]
				and ball["x"] <= self.games[self.room_name][1].paddle["x"] + self.games[self.room_name][1].paddle["width"]
			):
				print(f'choca en paleta 2: {ball["y"]} >= {self.games[self.room_name][0].paddle["y"]}')
				ball["vy"] *= -1
				ball["y"] = self.games[self.room_name][1].paddle["y"] - ball["size"]
			
			# Enviar la nueva posición de la pelota a los clientes
			await self.channel_layer.group_send(self.room_group_name, {
					"type": "ball_update",
					"ball": ball,
					"score": {
						"a": self.games[self.room_name][0].paddle["score"],
						"b": self.games[self.room_name][1].paddle["score"]
					}
				}
			)
			await asyncio.sleep(0.03)  # Controla la velocidad de actualización

	async def ball_update(self, event):
		# Enviar la posición de la pelota a los clientes
		await self.send(text_data=json.dumps({"action": "ball", "ball": event["ball"], "score": event["score"]}))
	
	async def finish_game(self, event):
		# Enviar la posición de la pelota a los clientes
		await self.send(text_data=json.dumps({"action": "finish", "winner": event["winner"]}))