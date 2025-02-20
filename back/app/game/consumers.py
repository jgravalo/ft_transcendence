import json
import uuid
import time
from channels.generic.websocket import AsyncWebsocketConsumer

import logging
import json
import sys
# TODO: make it a module
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "filename": record.filename,
            "funcName": record.funcName,
            "lineno": record.lineno
        }
        return json.dumps(log_record)
logger = logging.getLogger("game-back")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

waiting_list = []
playing_list = []
matches = []

class Match(AsyncWebsocketConsumer):
    players = {}

    async def connect(self):
        await self.accept()
        self.player_id = None
        logger.info("Connection Received.")

    async def receive(self, text_data):
        data = json.loads(text_data)
        # JOIN TO REM
        if data.get("step") == "join":
            logger.info("Join game request.")
            self.status = 'wait'
            self.canvas = data.get("canvas")
            self.player_info = data.get("player")
            self.player_id = str(uuid.uuid4())
            self.username = data.get("username")
            if self.username == 'unregistered':
                self.username = f'noName_{self.player_id}'
            self.game_mode = data.get("mode")
            logger.info(self.game_mode)
            # MODE REMOTE IA:
            if self.game_mode == 'remote-ai':
                print("llegamos aquí??")
                logger.info("Response remote-ai request. Start.")
                await self.send(text_data=json.dumps({
                    "step": "start",
                    "opponentName": 'HAL-42',
                }))
            if self.game_mode != 'remote-ai':
                # ENCONTRAR USUARIO EN WAITING LIST O PONERLO EN WAITING LIST
                if (len(waiting_list) > 0):
                    matches.append([self, waiting_list[0]])
                    waiting_list.remove(waiting_list[0])
                else:
                    waiting_list.append(self)

        elif data.get("step") == "move":
            if self.game_mode == 'remote-ai':
                await self.opponentIA(data.get("position"), data.get("ball"))
            # player_id = data.get("player")
            # if player_id in self.players:
            #     self.players[player_id]["x"] = data["x"]
            #     await self.broadcast_game_state()

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

    async def opponentIA(self, position, ball):
        centerIA = position['x'] + position['width'] / 2
        if centerIA < ball['x'] - 10:
            position['x'] = position['x'] + 3
        elif centerIA > ball['x'] + 10:
            position['x'] = position['x'] - 3
        position['x'] = max(0, min(position['x'], self.canvas['width'] - position['width']))
        await self.send(text_data=json.dumps({
            "step": "move",
            "position": position['x']
        }))