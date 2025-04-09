import json
import asyncio
import uuid
from asgiref.sync import sync_to_async
from django.apps import apps
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from channels.db import database_sync_to_async

class PongConsumer(AsyncWebsocketConsumer):
	games = {}  # Lista para almacenar jugadores
	ball = {}  # Lista para almacenar jugadores
	
	async def find_available_room(self):
		""" Busca una sala con espacio disponible (1 jugador) """
		print('in find_available_room')
		print(f'len games = {len(self.games)}')
		for room, game_list in self.games.items():
			# print(f'room {room}; len1: {len(game_list)}; len2: {len(self.games[room])}')
			# Si hay un solo jugador, la sala tiene espacio
			# print(f'room[:7] = {room[:7]}')
			# if len(game_list) == 1 and room[:7] != 'game_re': # Protegemos de partidas restringidas
			if len(game_list) == 1 and room[:7] == 'game_ra': # Protegemos de partidas restringidas
				return room
		return None # No hay salas disponibles con espacio

	async def connect(self):
		""" if self.connected == True:
			self.close()
			print('FUERA')
			return
		self.connected = True  # Lo definís vos """
		if self.scope['user'].is_authenticated:
			if self.scope['user'].is_playing:
				print('YA ESTA JUGANDO')
				self.close()
				print('FUERA')
				return
			else:
				self.scope['user'].is_playing = True
				await database_sync_to_async(self.scope['user'].save)()
				print('EMPIEZA A JUGAR')
		else:
			self.close()
		available_room = await self.find_available_room()
		User = apps.get_model('users', 'User')

		# Para hacer el otro usuario restringido

		print('set game')
		self.user2 = parse_qs(self.scope["query_string"].decode()).get("user", [None])[0]
		self.room_name = parse_qs(self.scope["query_string"].decode()).get("room", [None])[0]
		print(f'ROOM NAME = {self.room_name}')
		try:
			print(f'user2 before: {self.user2}')
			self.user2 = await sync_to_async(User.objects.get)(id=self.user2)
			print(f'user2 before: {self.user2.id}')
		except:
			self.user2 = None  # O cualquier valor predeterminado
		# Obtener la sala desde la URL o algún identificador
		print("self.room_name =", self.room_name)

		self.is_tournament = False
		if self.user2:
			print('CREATE RESTRICTED GAME')
			self.room_name = f"game_re{uuid.uuid4().hex[:8]}"
			self.games[self.room_name] = []  # Nueva sala
			print(f'invite {self.user2.username}')
			await sync_to_async(self.user2.invite)(self.user2, self.room_name)
		elif self.room_name: # in self.games:
			print('ADD TO RESTRICTED GAME')
			if self.room_name[:7] == 'game_to':
				if self.room_name not in self.games or not self.games[self.room_name]: # hacer algo si la sala no existe o está vacía
					self.games[self.room_name] = []  # Nueva sala
				self.is_tournament = True
				self.tournament_id = parse_qs(self.scope["query_string"].decode()).get("tournament", [None])[0]
				self.round = int(parse_qs(self.scope["query_string"].decode()).get("round", [None])[0])
				print(f'TOURNAMENT ID = {self.tournament_id}')
				print(f'round = {self.round}')
			pass
		elif available_room:
			print('ADD TO RANDOM GAME')
			self.room_name = available_room  # Unirse a la sala con espacio
			print('room available')
		else:
			print('CREATE RANDOM GAME')
			# self.room_name = self.scope["url_route"]["kwargs"]["room_name"]  # Nueva sala
			self.room_name = f"game_ra{uuid.uuid4().hex[:8]}"
			self.games[self.room_name] = []
			print('new room')

		print(f'room_name in connect = {self.room_name}')
		self.room_group_name = f'private_{self.room_name}'
		print('set user')
		self.user = self.scope['user']
		self.name = self.user.username if self.user.is_authenticated else f"Customplayer{len(self.games[self.room_name]) + 1}"
		self.role = f"player{len(self.games[self.room_name]) + 1}"
		self.paddle = {"width": 80, "height": 10, "score": 0,
			"x": 150, "y": 10 if len(self.games[self.room_name]) == 0 else 580}
		print(f'user {self.name}: {self.user.id}, role:', self.role)
		# print('paddle[y]:', self.paddle['y'])
		# print(f'user: {self.name} {self}')
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
		print(f'room_name in disconnect = {self.room_name} by {self.name}')
		self.ball[self.room_name]['connect'] = False
		if self in self.games[self.room_name]:
			for player in self.games[self.room_name]:
				if self != player:
					await player.send(text_data=json.dumps({
						"action": "finish",
						"winner": player.name
					}))
				# player.connected = False
				player.user.is_playing = False
				await database_sync_to_async(self.scope['user'].save)()
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
						winner = self.games[self.room_name][0].user
					elif self.games[self.room_name][1].paddle["score"] >= ball["max-score"]:
						winner = self.games[self.room_name][1].user
					
					# guarda en db
					if (self.games[self.room_name][0].user.is_authenticated and
					self.games[self.room_name][1].user.is_authenticated):
						self.games[self.room_name][0].user.is_playing = False
						await database_sync_to_async(self.games[self.room_name][0].user.save)()
						self.games[self.room_name][1].user.is_playing = False
						await database_sync_to_async(self.games[self.room_name][1].user.save)()

						# self.games[self.room_name][0].connected = False
						# self.games[self.room_name][1].connected = False
						Match = apps.get_model('game', 'Match')
						game = await sync_to_async(Match.objects.create)(
							player1=self.games[self.room_name][0].user,
							player2=self.games[self.room_name][1].user,
							score_player1=self.games[self.room_name][0].paddle["score"],
							score_player2=self.games[self.room_name][1].paddle["score"],
						)
						if self.is_tournament:
							Round = apps.get_model('game', 'Round')
							# cualquier filtro extra,
							# modificar User.invite() y remote_game() en py
							# y gameRemote() en js
							round = await sync_to_async(Round.objects.get)(tournament__id=self.tournament_id, number=self.round)
							await sync_to_async(round.matches.add)(game)
							if round.number == 2:
								round.tournament.winner = winner
								await sync_to_async(round.tournament.save)()
							else:
								next_round = await sync_to_async(Round.objects.get)(tournament__id=self.tournament_id, number=self.round / 2)
								await sync_to_async(next_round.add_player)(winner)

					await self.channel_layer.group_send(self.room_group_name, {
						"type": "finish_game",
						"winner": winner.username
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
				# print(f'choca en paleta 1: {ball["y"]} <= {self.games[self.room_name][0].paddle["y"]} + {self.games[self.room_name][0].paddle["height"]}')
				ball["vy"] *= -1  # Invierte la dirección vertical
				ball["y"] = self.games[self.room_name][0].paddle["y"] + self.games[self.room_name][0].paddle["height"] # Evita quedarse pegada
			# 🏓 Verificar colisión con la paleta del jugador 2
			elif (
				ball["y"] # + self.ball["size"] / 2
				>= self.games[self.room_name][1].paddle["y"]
				and ball["x"] >= self.games[self.room_name][1].paddle["x"]
				and ball["x"] <= self.games[self.room_name][1].paddle["x"] + self.games[self.room_name][1].paddle["width"]
			):
				# print(f'choca en paleta 2: {ball["y"]} >= {self.games[self.room_name][0].paddle["y"]}')
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