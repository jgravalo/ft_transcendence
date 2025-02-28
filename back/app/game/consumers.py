import asyncio
import json
import uuid
import time
from cgitb import reset

from channels.generic.websocket import AsyncWebsocketConsumer
import random
import math
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
        if hasattr(record, "corr"):
            log_record["corr"] = record.corr
        return json.dumps(log_record)
logger = logging.getLogger("game-back")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

waiting_list = []
playing_list = []
matches = {}

CANVAS = {'width': 400, 'height': 800}
PLAYER_ROLES = ['player1', 'player2']


# random.shuffle(keys)
#
# player_a = keys[0]
# player_b = keys[1]

# print(player_a, player_b)

# def reset_ball(ball, canvas_width, canvas_height):
#     ball["x"] = canvas_width / 2
#     ball["y"] = canvas_height / 2
#
#     angle = (random.random() - 0.5) * math.pi / 8
#
#     ball["speedX"] = ball["baseSpeed"] * math.sin(angle)
#     ball["speedY"] = ball["baseSpeed"] * math.cos(angle) * (1 if random.random() > 0.5 else -1)
import random
import math

class GameSession:
    roles = ['player1', 'player2']
    no_name = {'player1': 'shyGuy1', 'player2': 'shyGuy2'}
    users = {}
    match_id = None
    player1 = None
    player2 = None
    players = []
    paddles = {}
    playing = False
    def __init__(self, match_id, players, width=400, height=800):
        self.canvas = {'width': width, 'height': height}
        random.shuffle(self.roles)
        self.users[self.roles[0]] = players[0]
        self.users[self.roles[1]] = players[1]
        self.players = players
        self.match_id = match_id
        for key, player in self.users.items():
            if self.users[key].username == 'unregistered':
                self.users[key].username = self.no_name[key]
        self.ball = {
            'x': width / 2,
            'y': height / 2,
            'size': 15,
            'speedX': 4,
            'speedY': 4,
            'baseSpeed': 4
        }
        self.paddles = {
            "player1": {"role": "player1", "x": width / 2 - 50, "y": height - 80, "width": 100, "height": 15, "score": 0, "speedModifier": 1},
            "player2": {"role": "player2", "x": width / 2 - 50, "y": 60, "width": 100, "height": 15, "score": 0, "speedModifier": 1}
        }
        self.power_ups = []
        self.collision_count = 0
        self.collision_threshold = 5  # Número de colisiones para generar un power-up

    # async def start_game_loop(self):
    #     while True:
    #         self.game.update_ball_position()
    #         await self.send_game_state()
    #         await asyncio.sleep(0.016)

    async def send_start_screen(self):
        init_time = time.time()
        while time.time() < init_time + 60:
            for key, player in self.users.items():
                opp = 'player1' if key == 'player2' else 'player2'
                await player.send(text_data=json.dumps({
                    "step": "ready",
                    "playerRole": key,
                    "player": self.users['player1'],
                    "playerStart": self.players['player1'],
                    "opponentStart": self.players['player2'],
                    "opponent": self.users['player2'],
                    "opponentName": self.users[opp].username
                }))
                await asyncio.sleep(0.016)

    def get_role(self, player):
        for key, value in self.users.items():
                if value == player:
                    return key  # Retorna la primera clave encontrada
        return None

    def get_users(self):
        return self.users

    def reset_ball(self):
        """Reinicia la pelota en una posición aleatoria con un ángulo aleatorio."""
        self.ball["x"] = self.canvas['width'] / 2
        self.ball["y"] = self.canvas['height'] / 2
        angle = (random.random() - 0.5) * math.pi / 8
        self.ball["speedX"] = self.ball["baseSpeed"] * math.sin(angle)
        self.ball["speedY"] = self.ball["baseSpeed"] * math.cos(angle) * (1 if random.random() > 0.5 else -1)
        self.collision_count = 0
        return self.ball

    def update_ball_position(self):
        """Mueve la pelota y gestiona colisiones con paredes y paletas."""
        self.ball["x"] += self.ball["speedX"]
        self.ball["y"] += self.ball["speedY"]

        # Rebote en los bordes laterales
        if self.ball["x"] <= 0 or self.ball["x"] >= self.canvas["width"]:
            self.ball["speedX"] *= -1

        # Colisión con la paleta del jugador
        if self.check_collision(self.ball, self.paddles['player1']):
            self.ball["y"] = self.paddles['player1']["y"] - self.ball["size"]
            self.ball["speedY"] = -abs(self.ball["baseSpeed"] * self.paddles['player1']["speedModifier"])
            self.collision_count += 1

        # Colisión con la paleta del oponente
        elif self.check_collision(self.ball, self.paddles['player2']):
            self.ball["y"] = self.paddles['player2']["y"] + self.paddles['player2']["height"]
            self.ball["speedY"] = abs(self.ball["baseSpeed"] * self.paddles['player2']["speedModifier"])
            self.collision_count += 1

        # Punto para el oponente
        if self.ball["y"] >= self.canvas["height"]:
            self.paddles['player2']["score"] += 1
            self.reset_ball()

        # Punto para el jugador
        elif self.ball["y"] <= 0:
            self.paddles['player1']["score"] += 1
            self.reset_ball()

        # Generar power-ups si se cumplen las condiciones
        self.generate_power_up()
        return self.ball

    def check_collision(self, ball, paddle):
        """Verifica si la pelota colisiona con una paleta."""
        collision = (
                ball["x"] > paddle["x"] and
                ball["x"] < paddle["x"] + paddle["width"] and
                ball["y"] + ball["size"] / 2 > paddle["y"] and
                ball["y"] - ball["size"] / 2 < paddle["y"] + paddle["height"]
        )
        if collision:
            hit_point = ball['x'] - (paddle['x'] + paddle['width'] / 2)
            normalized_hp = hit_point / (paddle['x'] / 2)
            ball['speedX'] = normalized_hp * 6
        return collision

    def generate_power_up(self):
        """Genera un power-up después de cierta cantidad de colisiones."""
        if self.collision_count >= self.collision_threshold and len(self.power_ups) == 0:
            power_up = {
                "x": random.randint(50, self.canvas["width"] - 50),
                "y": random.randint(200, self.canvas["height"] - 200),
                "type": random.choice([">>", "<<"]),
                "active": False
            }
            self.power_ups.append(power_up)
            self.collision_count = 0  # Reiniciar el contador

    def apply_power_up(self, player_id, power_up_type):
        """Aplica un power-up a un jugador."""
        player = self.players[player_id]
        if power_up_type == ">>":
            player["width"] = min(player["width"] + 10, self.canvas["width"] - 45)
            player["speedModifier"] = max(player["speedModifier"] - 0.1, 0.8)
        elif power_up_type == "<<":
            player["width"] = max(player["width"] - 10, 45)
            player["speedModifier"] = min(player["speedModifier"] + 0.1, 1.2)

    def check_power_up_collisions(self):
        """Verifica si un jugador o la pelota recoge un power-up."""
        for power_up in self.power_ups:
            if (
                    self.ball["x"] < power_up["x"] + 15 and
                    self.ball["x"] + self.ball["size"] > power_up["x"] and
                    self.ball["y"] < power_up["y"] + 15 and
                    self.ball["y"] + self.ball["size"] > power_up["y"]
            ):
                self.apply_power_up("player1", power_up["type"])
                self.power_ups.remove(power_up)

    def update_paddle_position(self, role, position):
        logger.warning(f"updating {role}")
        self.paddles[role]['x'] = position

    def get_game_state(self):
        """ Retorna el estado del juego """
        return self.paddles

    async def start_game_loop(self):
        while True:
            game_info = matches[self.match_id]
            paddles = game_info["game"].get_game_state()
            for role in PLAYER_ROLES:
                opp = 'player1' if role == 'player2' else 'player2'
                await game_info["players"][role].send(text_data=json.dumps({
                    "step": "update",
                    "playerRole": role,
                    "player": paddles[role],
                    "opponent": paddles[opp]
                }))
                # self.playing = True
                # self.game.update_ball_position()
                # await self.send_game_state()
                await asyncio.sleep(0.016)

    # def get_game_state(self):
    #     """Devuelve el estado actual del juego para ser enviado al frontend."""
    #     return {
    #         "ball": self.ball,
    #         "players": self.players,
    #         "powerUps": self.power_ups
    #     }


class Match(AsyncWebsocketConsumer):
    cnn_id = None
    match_id = None
    players = {}
    active_match = []
    status = None
    canvas = {'width': 400, 'height': 800}
    opponent = None
    opponent_name = None
    username = None
    player_role = None
    other_list = []
    global matches
    ball = {
        'x': canvas['width'] / 2,
        'y': canvas['height'] / 2,
        'size': 15,
        'speedX': 4,
        'speedY': 4,
        'baseSpeed': 4
    }
    opponent_ball = {
        'x': canvas['width'] / 2,
        'y': canvas['height'] / 2,
        'size': 15,
        'speedX': 4,
        'speedY': 4,
        'baseSpeed': 4
    }

    async def connect(self):
        await self.accept()
        self.cnn_id = str(uuid.uuid4())
        logger.info(f"Connection established", extra={"corr": self.cnn_id})

    async def receive(self, text_data):
        """
        Process received message.

        :param self: connection instance.
        :param text_data: json object received.
        """
        data = json.loads(text_data)
        # Join to remote mode
        if data.get("step") == "join":
            if data.get("mode") != 'remote':
                logger.error(f"Connection {self.cnn_id} requested a wrong game mode.", extra={"corr": self.cnn_id})
                await self.send(text_data=json.dumps({
                    "step": "error",
                    "detail": "Wrong game mode"
                }))
                await self.close(code=4001)
            self.username = data.get("username")
            if self.username == 'unregistered':
                random_number = str(random.randint(1, 999)).zfill(3)
                self.username = f'shy_guy-{random_number}'
            logger.info("Join remote game request.", extra={"corr": self.cnn_id})
            logger.info(f"Players waiting to play: {len(waiting_list)}", extra={"corr": self.cnn_id})
            if waiting_list:
                logger.info(f"Players Waiting. Create a new game.", extra={"corr": self.cnn_id})
                # Get Opponent to the match.
                self.opponent = waiting_list.pop(0)
                # start a new GameSession
                self.match_id = str(uuid.uuid4())
                self.opponent.match_id = self.match_id
                game = GameSession(self.match_id, [self, self.opponent])
                logger.info(f"Match Created.", extra={"corr": self.match_id})
                logger.info(f"Players {self.username} - {self.opponent.username}", extra={"corr": self.match_id})
                self.player_role = game.get_role(self)
                self.opponent.player_role = game.get_role(self.opponent)
                logger.info(f'Random roles assigned', extra={"corr": self.match_id})
                matches[self.match_id] = {
                    "players": {
                        "player1": self if self.player_role == "player1" else self.opponent,
                        "player2": self if self.player_role == "player2" else self.opponent
                    },
                    "game": game
                }
                await self.send_start_screen(game)
            else:
                await self.send(text_data=json.dumps({
                    "step": "wait",
                    "ball": self.reset_ball()
                }))
                waiting_list.append(self)

        elif data.get("step") == "update":
            logger.info(f"hello {data}")
            role = data.get("role")
            matches[self.match_id]['game'].update_paddle_position(role, data.get('position'))
            game_info = matches[self.match_id]
            paddles = game_info["game"].get_game_state()
            ball = game_info["game"].update_ball_position()
            for role in PLAYER_ROLES:
                opp = 'player1' if role == 'player2' else 'player2'
                await game_info["players"][role].send(text_data=json.dumps({
                    "step": "update",
                    "playerRole": role,
                    "player": paddles[role],
                    "opponent": paddles[opp],
                    "ball": ball
                }))

    async def start_game_loop(self):
        while True:
            game_info = matches[self.match_id]
            paddles = game_info["game"].get_game_state()
            for role in PLAYER_ROLES:
                opp = 'player1' if role == 'player2' else 'player2'
                await game_info["players"][role].send(text_data=json.dumps({
                    "step": "update",
                    "playerRole": role,
                    "player": paddles[role],
                    "opponent": paddles[opp]
                }))
                # self.playing = True
                # self.game.update_ball_position()
                # await self.send_game_state()
                await asyncio.sleep(0.016)

    async def send_start_screen(self, game):
        logger.info('Send start screen messages', extra={"corr": self.match_id})
        await self.broadcast_message("Be prepare to fight!")
        await asyncio.sleep(3)
        await self.broadcast_message("2 seconds to go!")
        await asyncio.sleep(2)
        ball = game.reset_ball()
        await self.broadcast_message("GO!", "go")
        await asyncio.sleep(0.2)
        logger.info('Prepare message sent.', extra={"corr": self.match_id})


    async def broadcast_message(self, message, step="ready", ball=None):
        game_info = matches[self.match_id]
        players_default = game_info["game"].get_game_state()
        for role in PLAYER_ROLES:
            opp = 'player1' if role == 'player2' else 'player2'
            await game_info["players"][role].send(text_data=json.dumps({
                "step": step,
                "message": message,
                "playerRole": game_info["players"][role].player_role,
                "opponentName": game_info["players"][opp].username,
                "player1": players_default["player1"],
                "player2": players_default["player2"],
                "ball": ball
            }))


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
        logger.warning(f"Client disconnected {close_code}")
        if (self.status == 'wait'):
            pass
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

    def reset_ball(self):
        self.ball["x"] = self.canvas['width'] / 2
        self.ball["y"] = self.canvas['height'] / 2

        angle = (random.random() - 0.5) * math.pi / 8

        self.ball["speedX"] = self.ball["baseSpeed"] * math.sin(angle)
        self.ball["speedY"] = self.ball["baseSpeed"] * math.cos(angle) * (1 if random.random() > 0.5 else -1)

    async def remote_game(self):
        pass

class MatchAI(AsyncWebsocketConsumer):
    """
    Remote AI handler.
    """
    cnn_id = None

    async def connect(self):
        """
        Accept a new connection.
        """
        await self.accept()
        self.cnn_id = str(uuid.uuid4())
        logger.info(f"Connection established", extra={"corr": self.cnn_id})

    async def receive(self, text_data):
        """
        Process received message.

        :param self: connection instance.
        :param text_data: json object received.
        """
        data = json.loads(text_data)
        mode = data.get("mode")

        if data.get("step") == "join":
            logger.info(f"Join AI game request.", extra={"corr": self.cnn_id})
            await self.send(text_data=json.dumps({
                "step": "start",
                "opponentName": 'HAL-42',
            }))
            logger.info(f"Response remote-ai request. Start.", extra={"corr": self.cnn_id})
            if mode != 'remote-ai':
                logger.error(f"Connection {self.cnn_id} requested a wrong game mode. {self.cnn_id}")
                await self.send(text_data=json.dumps({
                    "step": "error",
                    "detail": "Wrong game mode"
                }))
                await self.close(code=4001)
        elif data.get("step") == "move":
            await self.opponent_ia(data.get("position"), data.get("ball"))

        elif data.get("step") == "end":
            logger.info(f"AI Game Ended. Score {data.get('player_score')} - {data.get('opponent_score')}", extra={"corr": self.cnn_id})
            await self.close()

    async def opponent_ia(self, position, ball):
        center_ia = position['x'] + position['width'] / 2
        if center_ia < ball['x'] - 10:
            position['x'] = position['x'] + 3
        elif center_ia > ball['x'] + 10:
            position['x'] = position['x'] - 3
        position['x'] = max(0, min(position['x'], CANVAS['width'] - position['width']))
        await self.send(text_data=json.dumps({
            "step": "move",
            "position": position['x']
        }))