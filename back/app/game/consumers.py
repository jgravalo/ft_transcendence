import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PongConsumer(AsyncWebsocketConsumer):
	players = []  # Lista para almacenar jugadores

	async def connect(self):
		if len(self.players) < 2:
			# username = self.scope['user'].username
			# if user.username == AnonymousUser:
			# 	username = f"Anonymous{len(self.players) + 1}"
			# role = f"player{len(self.players) + 1}"
			self.role = "player1" if len(self.players) == 0 else "player2"
			print('role:', self.role)
			self.players.append(self)
			await self.accept()
			await self.send(text_data=json.dumps({"action": "set-player", "role": self.role}))

			if len(self.players) == 2:
				# Cuando haya dos jugadores, avísales que pueden empezar
				for player in self.players:
					await player.send(text_data=json.dumps({"action": "start", "role": self.role}))
		else:
			await self.close()  # Si hay más de 2 jugadores, cierra la conexión

	async def disconnect(self, close_code):
		if self in self.players:
			self.players.remove(self)

	async def receive(self, text_data):
		data = json.loads(text_data)
        # role = data['role']
		# print('text_data: ', text_data)
		# Reenvía los datos al otro jugador
		for player in self.players:
			if player != self:
				await player.send(text_data=json.dumps(data))
