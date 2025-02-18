import json
import uuid
import time
from channels.generic.websocket import AsyncWebsocketConsumer

class Match(AsyncWebsocketConsumer):
    players = {}  # Diccionario para almacenar jugadores conectados
    async def connect(self):
        await self.accept()
        self.player_id = None  # Se asignará cuando el jugador se una
        print("✅ Cliente conectado al WebSocket.")

    async def testIA(self):
        count = 0
        while count < 3:
            time.sleep(1)
            count += 1
            await self.send(text_data=json.dumps({
                "step": "ia",
                "hello": "hola"
            }))

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("step") == "join":
            # Crear log para el join... otros procesos no deberían ser necesarios.
            # Asigna un ID al jugador si no tiene
            self.player_id = str(uuid.uuid4())
            self.username = data.get("username")
            if self.username == 'unregistered':
                self.username = f'noName_{self.player_id}'
            self.game_mode = data.get("mode")
            # self.player_id = "player1" if "player1" not in self.players else "player2"
            self.players[self.player_id] = {"x": 200, "consumer": self}
            # print(f"{self.player_id} se ha unido al juego.")
            await self.send(text_data=json.dumps({
                "step": "wait",
                "player_name": self.username,
                "player_id": self.player_id
            }))
            if self.game_mode == 'remote-ia':
                await self.testIA()
            # Envía el estado actual al cliente
            # await self.send(text_data=json.dumps({
            #     "type": "update",
            #     "players": {player: {"x": info["x"]} for player, info in self.players.items()}
            # }))

        elif data.get("type") == "move":
            player_id = data.get("player")
            if player_id in self.players:
                self.players[player_id]["x"] = data["x"]
                await self.broadcast_game_state()

    async def broadcast_game_state(self):
        """Envía la actualización del estado del juego a todos los clientes."""
        message = {
            "type": "update",
            "players": {player: {"x": info["x"]} for player, info in self.players.items()}
        }
        await self.broadcast(message)

    async def broadcast(self, data):
        """Envía un mensaje a todos los jugadores conectados."""
        message = json.dumps(data)
        for player in self.players.values():
            await player["consumer"].send(text_data=message)

    async def disconnect(self, close_code):
        print(f"Cliente desconectado: {self.player_id}")
        if self.player_id and self.player_id in self.players:
            del self.players[self.player_id]
            print(f"Jugador {self.player_id} eliminado del juego.")
