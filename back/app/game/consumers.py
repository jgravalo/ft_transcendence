import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class PongConsumer(AsyncWebsocketConsumer):
	players = []  # Lista para almacenar jugadores
	ball = {"x": 300, "y": 200, "vx": 5, "vy": 5, "width": 400, "height": 600}  # Posición y velocidad de la pelota

	async def connect(self):
		if len(self.players) < 2:
			# username = self.scope['user'].username
			# if user.username == AnonymousUser:
			# 	username = f"Anonymous{len(self.players) + 1}"
			self.name = self.scope['user'].username
			self.role = f"player{len(self.players) + 1}"
			# self.role = "player1" if len(self.players) == 0 else "player2"
			print('role:', self.role)
			self.players.append(self)
			
			await self.accept()
			await self.send(text_data=json.dumps({"action": "set-player", "role": self.role}))

			if len(self.players) == 2:
				await self.channel_layer.group_add("pong_game", self.channel_name)
				print("🚀 Dos jugadores conectados. Iniciando el juego...")
				asyncio.create_task(self.start_game_loop())  # 🔥 Iniciar el bucle de la pelota
				
				# Cuando haya dos jugadores, avísales que pueden empezar
				for player in self.players:
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
			print('ball: x:', self.ball["x"], ', y:', self.ball["y"])

			# Rebote en las paredes superior e inferior
			if self.ball["y"] <= 0 or self.ball["y"] >= self.ball["height"]:
				self.ball["vy"] *= -1  # Invertir dirección en Y
			
			""" if self.ball["x"] <= 0 or self.ball["x"] >= self.ball["width"]:
				self.ball["vx"] *= -1  # Invertir dirección en Y """
			if (
				self.ball["x"] <= 0 or
				self.ball["x"] >= self.ball["width"]
				):
				self.ball["vx"] *= -1  # Invertir dirección en Y

			# Enviar la nueva posición de la pelota a los clientes
			await self.channel_layer.group_send(
				"pong_game",
				{"type": "ball_update", "ball": self.ball}
			)
			await asyncio.sleep(0.03)  # Controla la velocidad de actualización

	async def ball_update(self, event):
		# Enviar la posición de la pelota a los clientes
		await self.send(text_data=json.dumps({"action": "ball", "ball": event["ball"]}))
