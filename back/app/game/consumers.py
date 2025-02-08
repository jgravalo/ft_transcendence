import json
from channels.generic.websocket import AsyncWebsocketConsumer

class Match(AsyncWebsocketConsumer):
    players = {}  # Diccionario para almacenar jugadores conectados

    async def connect(self):
        await self.accept()
        print("✅ Cliente conectado al WebSocket.")

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Mensaje recibido: {data}")

        if data.get("type") == "join":
            player_id = data.get("player", f"player{len(self.players) + 1}")
            self.players[player_id] = {"x": 200}  # Posición inicial del jugador
            print(f"{player_id} se ha unido al juego. Total de jugadores: {len(self.players)}")

            # Si hay menos de 2 jugadores, enviar mensaje de espera
            if len(self.players) < 2:
                waiting_message = {
                    "type": "waiting",
                    "message": "Esperando a otro jugador..."
                }
                print(f"Enviando mensaje de espera: {waiting_message}")
                await self.send(text_data=json.dumps(waiting_message))

    async def broadcast_game_state(self):
        """Envia la actualización del estado del juego a todos los clientes."""
        message = json.dumps({
            "type": "update",
            "players": self.players,
        })
        await self.send_to_all(json.loads(message))

    async def send_to_all(self, data):
        """Envía un mensaje a todos los jugadores conectados."""
        message = json.dumps(data)
        for player in self.players.values():
            await self.send(text_data=message)

    async def disconnect(self, close_code):
        print(f"Cliente desconectado. Código: {close_code}")

        if close_code == 1001:
            print("⚠ La conexión WebSocket se cerró inesperadamente. Verifica si el cliente está perdiendo la conexión.")

        if self.players:
            for player_id in list(self.players.keys()):
                if self.players[player_id] == self:
                    del self.players[player_id]
                    print(f"Jugador {player_id} eliminado de la lista.")
                    break

