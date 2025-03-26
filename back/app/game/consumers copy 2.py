import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import uuid
import copy

class Game:
	def __init__(self):
		self.players = []
		self.ball = None
		self.finish = False

	def add_player(self, player):
		self.players.append(player)
		
	def delete_player(self, player):
		self.players.remove(player)

	def set_ball(self, ball):
		self.ball = ball

class PongConsumer(AsyncWebsocketConsumer):
	games = {} # Diccionario para almacenar partidas por id
	players = []  # Lista para almacenar jugadores
	ball = {"x": 300, "y": 200, "vx": 5, "vy": 5, "width": 400, "height": 600,
		"size": 10, "max-score": 2}  # Posición y velocidad de la pelota
	room_group_name = None

	async def connect(self):
		print('set user')
		self.user = self.scope['user']
		self.name = self.user.username if self.user.username != '' else f"Customplayer{len(self.players) + 1}"
		print(f'user \"{self.name}\": \"{self.user.id}\"')
		self.role = f"player{(len(self.players) % 2) + 1}"
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

		await self.accept()
		await self.send(text_data=json.dumps({"action": "set-player", "role": self.role}))

		if len(self.players) == 2:
			print('set group')
			self.room_name = f'game_{self.players[0].user.id}_{self.players[1].user.id}'
			self.room_group_name = f'private_{self.room_name}'
			print(f"🔗 Conectando a la sala {self.room_group_name}")

			# Añadir jugadores y configurar la pelota
			game = Game()
			game.add_player(self.players[0])
			game.add_player(self.players[1])
			game.set_ball(self.ball)  # Ejemplo de la pelota

			# self.game_id = f"game_{uuid.uuid4().hex[:8]}"
			# print('id:', self.game_id)  # Ejemplo: game_a1b2c3d4
			self.games[self.room_group_name] = game
			await self.channel_layer.group_add(self.room_group_name, self.channel_name)
			print("🚀 Dos jugadores conectados. Iniciando el juego...")
			asyncio.create_task(self.start_game_loop())  # 🔥 Iniciar el bucle de la pelota
			
			# Cuando haya dos jugadores, avísales que pueden empezar
			# for player in self.players:
			for player in self.games[self.room_group_name].players:
				player.room_group_name = self.room_group_name
				print(f'{player.role} paddle[y]:', player.paddle['y'])
				print(f'user1 \"{self.games[self.room_group_name].players[0].name}\": \"{self.games[self.room_group_name].players[0].user.id}\"')
				print(f'user2 \"{self.games[self.room_group_name].players[1].name}\": \"{self.games[self.room_group_name].players[1].user.id}\"')
				await self.channel_layer.group_add(self.room_group_name, player.channel_name)
				await player.send(text_data=json.dumps(
					{
					"action": "start",
					"role": player.role,
					"player1": self.games[self.room_group_name].players[0].name,
					"player2": self.games[self.room_group_name].players[1].name
					}))
			# self.players = []
			# self.players.remove(self.players[0])
			# self.players.remove(self.players[1])
	# else:
	#	await self.close()  # Si hay más de 2 jugadores, cierra la conexión
	async def disconnect(self, close_code):
		if self.players[0].paddle["score"] >= self.ball["max-score"]:
			winner =  self.players[0].name
		elif self.players[1].paddle["score"] >= self.ball["max-score"]:
			winner =  self.players[1].name
		await self.channel_layer.group_send(self.room_group_name, {
			"type": "finish_game",
			"winner": winner
		})
		print(f"❌ Desconectando de {self.room_group_name}")
		await self.channel_layer.group_discard(
			self.room_group_name,
			self.channel_name
		)
		""" for player in self.players:
		# for player in self.games[self.room_group_name].players:
			if player.role != self.role:
				print('envia desconexion al otro')
				player.send(text_data=json.dumps({
					"action": "finish",
					"winner": player.name
					})) """

		if self in self.players:
			print(f'{self.role} has been disconnected')
			self.players.remove(self)
		# if self in self.games[self.room_group_name].players:
		# 	self.games[self.room_group_name].delete_player(self)

	async def receive(self, text_data):
		data = json.loads(text_data)
		self.paddle['x'] = data['x']
		# Reenvía los datos al otro jugador
		for player in self.games[self.room_group_name].players:
			if player != self:
				await player.send(text_data=json.dumps(data))

	async def start_game_loop(self):
		# self.players = self.games[self.room_group_name].players
		# # players = self.games[self.room_group_name].players
		# self.ball = self.games[self.room_group_name].ball
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
					self.games[self.room_group_name].finish = True
					if self.players[0].paddle["score"] >= self.ball["max-score"]:
						winner =  self.players[0].name
					elif self.players[1].paddle["score"] >= self.ball["max-score"]:
						winner =  self.players[1].name
					await self.channel_layer.group_send(self.room_group_name, {
						"type": "finish_game",
						"winner": winner
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
		await self.send(text_data=json.dumps({"action": "finish", "winner": event["winner"]}))
