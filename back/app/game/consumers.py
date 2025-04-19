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
		for room, game_list in self.games.items():
			if len(game_list) == 1 and room[:7] == 'game_ra': # Protegemos de partidas restringidas
				return room
		return None # No hay salas disponibles con espacio

	async def wait_for_opponent(self):
		while len(self.games[self.room_name]) < 2:
			await asyncio.sleep(0.1)

	async def connect(self):
		# if self.scope['user'].is_authenticated:
		# 	if self.scope['user'].is_playing:
		# 		print(f"JUGADOR REPETIDO = {self.scope['user'].username}")
		# 		await self.close()
		# 		print('FUERA')
		# 		return
		# 	else:
		# 		self.scope['user'].is_playing = True
		# 		await database_sync_to_async(self.scope['user'].save)()
		# 		print(f"NUEVO JUGADOR = {self.scope['user'].username} playing: {self.scope['user'].is_playing}")
		# else:
		# 	await self.close()
		available_room = await self.find_available_room()
		User = apps.get_model('users', 'User')

		# Para hacer el otro usuario restringido

		self.room_name = parse_qs(self.scope["query_string"].decode()).get("room", [None])[0]
		self.user2 = parse_qs(self.scope["query_string"].decode()).get("user", [None])[0]
		try:
			self.user2 = await sync_to_async(User.objects.get)(id=self.user2)
		except:
			self.user2 = None  # O cualquier valor predeterminado
		# Obtener la sala desde la URL o algún identificador
		print(f"self.room_name: {self.room_name}")

		self.is_tournament = False
		self.is_playing = True
		if self.user2:
			print('CREATE RESTRICTED GAME')
			self.room_name = f"game_re{uuid.uuid4().hex[:8]}"
			self.games[self.room_name] = []  # Nueva sala
			print(f'invite {self.user2.username}')
			await sync_to_async(self.user2.invite)(self.user2, self.room_name)
		elif self.room_name: # in self.games:
			# print('ADD TO RESTRICTED GAME')
			if self.room_name[:7] == 'game_to':
				print('🧪 TORNEO DETECTADO')
				self.is_tournament = True
				self.tournament_id = parse_qs(self.scope["query_string"].decode()).get("tournament", [None])[0]
				self.round = int(parse_qs(self.scope["query_string"].decode()).get("round", [None])[0])
				print(f'TOURNAMENT ID = {self.tournament_id}, ROUND = {self.round}')

				# Si la sala existe y hay espacio, me uno
				if self.room_name not in self.games:
					print('✅ CREANDO NUEVA SALA DE TORNEO')
					self.games[self.room_name] = []
				elif len(self.games[self.room_name]) >= 2:
					print('❌ SALA DE TORNEO YA COMPLETA')
					await self.close()
					return
				else:
					print('🔗 UNIÉNDOSE A SALA DE TORNEO EXISTENTE')
			pass
		elif available_room:
			print('ADD TO RANDOM GAME')
			self.room_name = available_room  # Unirse a la sala con espacio
			# print('room available')
		else:
			print('CREATE RANDOM GAME')
			# self.room_name = self.scope["url_route"]["kwargs"]["room_name"]  # Nueva sala
			self.room_name = f"game_ra{uuid.uuid4().hex[:8]}"
			self.games[self.room_name] = []
			# print('new room')

		# print(f'room_name in connect = {self.room_name}')
		self.room_group_name = f'private_{self.room_name}'
		# print('set user')
		self.user = self.scope['user']
		self.name = self.user.username if self.user.is_authenticated else f"Customplayer{len(self.games[self.room_name]) + 1}"
		self.role = f"player{len(self.games[self.room_name]) + 1}"
		self.paddle = {
			"width": 10,
			"height": 50,
			"score": 0,
			"x": 10 if len(self.games[self.room_name]) == 0 else 480,  # 10px from left or right edge
			"y": (250 - 50) // 2  # center vertically
		}
		print('role:', self.role)
		print('paddle[y]:', self.paddle['y'])
		print(f'user: {self.name} {self}')
		print(f'user {self.name}: {self.user.id}, role:', self.role)
		print(f'[DEBUG] Antes de append: {len(self.games[self.room_name])} jugadores en la sala {self.room_name}')
		self.games[self.room_name].append(self)
		print(f'[DEBUG] Después de append: {[p.user.username for p in self.games[self.room_name]]}')
		# self.ball[self.room_name] = {"x": 300, "y": 200, "vx": 5, "vy": 5,
		# 	"width": 400, "height": 600, "size": 10, "max-score": 3, "connect": True}
		self.vx_default = 4
		self.speed = 0.03
		self.ball[self.room_name] = {"x": 250, "y": 125, "vx": 4, "vy": 4,
			"width": 500, "height": 250, "size": 10, "max-score": 3, "connect": True}

		await self.accept()
		await self.send(text_data=json.dumps({"action": "set-player", "role": self.role}))

		if self.is_tournament and len(self.games[self.room_name]) == 1:
			try:
				await asyncio.wait_for(self.wait_for_opponent(), timeout=5)
			except asyncio.TimeoutError:
				# await self.send(text_data="No se encontró segundo jugador a tiempo.")
				await self.close()

		if len(self.games[self.room_name]) == 2:
			print(f'EMPIEZA EL PARTIDO !!! {self.room_name}: {self.games[self.room_name][0].user.username} vs {self.games[self.room_name][1].user.username}')
			# print('set ball')

			asyncio.create_task(self.start_game_loop())  # 🔥 Iniciar el bucle de la pelota

			# Cuando haya dos jugadores, avísales que pueden empezar
			for player in self.games[self.room_name]:
				# print(f'{player.role} paddle[y]:', player.paddle['y'])
				await self.channel_layer.group_add(self.room_group_name, player.channel_name)
				await player.send(text_data=json.dumps({
					"action": "start",
					"role": self.role,
					"player1": self.games[self.room_name][0].name,
					"player2": self.games[self.room_name][1].name
				}))

	async def disconnect(self, close_code):
		try: # por si hay un solo jugador y se desconecta.
			print(f'room_name in disconnect = {self.room_name} by {self.name}')
			self.ball[self.room_name]['connect'] = False # detiene la bola
			self.is_playing = False
		except:
			pass

	async def receive(self, text_data):
		# print(f'room_name in receive = {self.room_name}')
		data = json.loads(text_data)
		self.paddle['y'] = data['y']
		for player in self.games[self.room_name]:
			if player != self:
				await player.send(text_data=json.dumps(data))
	
	@sync_to_async
	def set_winner(self, round, winner):
		tournament = round.tournament
		tournament.winner = winner
		tournament.save()

	async def start_game_loop(self):
		ball = self.ball[self.room_name]
		p1 = self.games[self.room_name][0].paddle
		p2 = self.games[self.room_name][1].paddle
		margin = 2; # margin of error for collision

		print(f'room_name in ball = {self.room_name}')
		# Bucle que mueve la pelota y la sincroniza en los clientes
		while len(self.games[self.room_name]) == 2:
			ball["x"] += ball["vx"]
			ball["y"] += ball["vy"]

			# Rebote en las paredes superior e inferior
			if ball["y"] <= 0 or ball["y"] >= ball["height"]:
				ball["vy"] *= -1  # Invertir dirección en Y

			if (ball["x"] <= 0 or ball["x"] >= ball["width"]):
				if ball["x"] >= ball["width"]:
					p1["score"] += 1
				elif ball["x"] <= 0:
					p2["score"] += 1

				ball["vx"] *= -1  # Invertir dirección en X
				ball["x"] = ball["width"] / 2
				ball["y"] = ball["height"] / 2
				print(f'{p1["score"]}-{p2["score"]}')

				if (p1["score"] >= ball["max-score"] or
					p2["score"] >= ball["max-score"]):
					if p1["score"] >= ball["max-score"]:
						winner = self.games[self.room_name][0].user
					elif p2["score"] >= ball["max-score"]:
						winner = self.games[self.room_name][1].user
					
					# Send final ball & score state
					await self.channel_layer.group_send(self.room_group_name, {
						"type": "ball_update",
						"ball": ball,
						"score": {
							"a": p1["score"],
							"b": p2["score"]
						}
					})
					await self.set_finish(winner, p1["score"], p2["score"])
					# await self.set_finish()
					break
			if not self.ball[self.room_name]['connect']: # no se si es util
				print('DESCONEXION')
				for player in self.games[self.room_name]:
					print(f'user = {player.name} is playing = {player.is_playing}')
					if player.is_playing == True:
						winner = player.user
				if self.role == 'player1':
					await self.set_finish(winner, 0, 3)
				elif self.role == 'player2':
					await self.set_finish(winner, 3, 0)
				await self.close()
				break
			
			# 🏓 Verificar colisión con la paleta del jugador 1
			if (
				ball["x"] - ball["size"] / 2 <= p1["x"] + p1["width"] + margin and  # left edge overlap
				ball["y"] + ball["size"] / 2 >= p1["y"] - margin and               # vertical overlap
				ball["y"] - ball["size"] / 2 <= p1["y"] + p1["height"] + margin
			):
				print(f'collision with paddle 1')
				ball["vx"] *= -1  # Invert horizontal direction
				# self.speed += 0.01
				ball["vx"] += 0.1  # Increase speed
				ball["x"] = p1["x"] + p1["width"] + margin + ball["size"] / 2  # Reposition to avoid sticking
			
			# 🏓 Verificar colisión con la paleta del jugador 2
			if (
				ball["x"] + ball["size"] / 2 >= p2["x"] - margin and
				ball["y"] + ball["size"] / 2 >= p2["y"] - margin and
				ball["y"] - ball["size"] / 2 <= p2["y"] + p2["height"] + margin
			):
				print(f'collision with paddle 2')
				ball["vx"] *= -1
				# self.speed += 0.01
				ball["vx"] -= 1  # Increase speed
				ball["x"] = p2["x"] - margin - ball["size"] / 2
			
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
			# await asyncio.sleep(0.03)  # Controla la velocidad de actualización
			await asyncio.sleep(self.speed)  # Controla la velocidad de actualización
	
	# @sync_to_async
	async def set_finish(self, winner, score1, score2):
	# async def set_finish(self):
		p1 = self.games[self.room_name][0].paddle
		p2 = self.games[self.room_name][1].paddle
		# guarda en db
		if (self.games[self.room_name][0].user.is_authenticated and
		self.games[self.room_name][1].user.is_authenticated):
			self.games[self.room_name][0].user.is_playing = False
			await database_sync_to_async(self.games[self.room_name][0].user.save)()
			self.games[self.room_name][1].user.is_playing = False
			await database_sync_to_async(self.games[self.room_name][1].user.save)()
			Match = apps.get_model('game', 'Match')
			Round = apps.get_model('game', 'Round')
			game = await sync_to_async(Match.objects.create)(
				player1=self.games[self.room_name][0].user,
				player2=self.games[self.room_name][1].user,
				score_player1=score1,
				score_player2=score2,
				# score_player1=p1["score"],
				# score_player2=p2["score"],
			)
			print(f'WINNER: {winner.username}')
			if self.is_tournament:
				round = await sync_to_async(Round.objects.get)(tournament__id=self.tournament_id, number=self.round)
				await sync_to_async(round.matches.add)(game)
				if round.number == 2:
					# round.tournament.winner = winner
					await self.set_winner(round, winner)
					await sync_to_async(round.tournament.save)()
				else:
					next_round = await sync_to_async(Round.objects.get)(tournament__id=self.tournament_id, number=self.round / 2)
					await sync_to_async(next_round.add_player)(winner)

		await self.channel_layer.group_send(self.room_group_name, {
			"type": "finish_game",
			"winner": winner.username
		})

	async def ball_update(self, event):
		# Enviar la posición de la pelota a los clientes
		await self.send(text_data=json.dumps({"action": "ball", "ball": event["ball"], "score": event["score"]}))
	
	async def finish_game(self, event):
		# Enviar la posición de la pelota a los clientes
		await self.send(text_data=json.dumps({"action": "finish", "winner": event["winner"]}))
		await self.close()