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


class GameSession:
    """
    Game Session class to control and update the game.
    """
    roles = ['player1', 'player2']
    users = {}
    match_id = None
    players = []
    paddles = {}
    playing = False
    ball = {}
    # ---
    power_ups = []
    power_up_size = None
    power_up_act_dist = None
    collision_count = 0
    collision_threshold = 2
    collision_to_points = 0
    def __init__(self, match_id, players, width=400, height=800):
        """
        Init method to GameSession class

        :param match_id: unique id to the match.
        :param players: a list of the players involved.
        :param width: canvas width. Optional.
        :param height: canvas height. Optional.
        """
        self.canvas = {'width': width, 'height': height}
        # Assign randomly roles to players.
        random.shuffle(self.roles)
        self.users[self.roles[0]] = players[0]
        self.users[self.roles[1]] = players[1]

        self.players = players
        self.match_id = match_id
        self.ball = {
            'x': width / 2,
            'y': height / 2,
            'size': 15,
            'speedX': float(4),
            'speedY': float(4),
            'baseSpeed': float(4)
        }
        self.power_up_size = self.ball['size'] * 1.5
        self.power_up_act_dist = self.power_up_size * 3
        self.paddles = {
            "player1": {
                "role": "player1",
                "x": width / 2 - 50,
                "y": height - 80,
                "width": 100,
                "height": 15,
                "score": 0,
                "points": 0,
                "speedModifier": 1
            },
            "player2": {
                "role": "player2",
                "x": width / 2 - 50,
                "y": 60,
                "width": 100,
                "height": 15,
                "score": 0,
                "points": 0,
                "speedModifier": 1
            }
        }

    def get_role(self, player):
        """
        Return the random role assign to a given player instance.

        :param player:
        :return: role assigned. None otherwise.
        """
        for key, value in self.users.items():
                if value == player:
                    return key
        return None

    def reset_ball(self):
        """
        Reset ball position.
        A new ball will be set at the middle of the field and a random
        angle is used to start.
        """
        self.ball["x"] = self.canvas['width'] / 2
        self.ball["y"] = self.canvas['height'] / 2
        angle = (random.random() - 0.5) * math.pi / 8
        self.ball["speedX"] = self.ball["baseSpeed"] * math.sin(angle)
        self.ball["speedY"] = self.ball["baseSpeed"] * math.cos(angle) * (1 if random.random() > 0.5 else -1)
        self.collision_count = 0

    def update_ball_position(self):
        """
        Move the ball around the field, and check for collision.

        A collision against a wall will modify its trajectory.
        A collision against a paddle will return the ball.
        A collision against any end of field, will update the score.
        """
        self.ball["x"] += self.ball["speedX"]
        self.ball["y"] += self.ball["speedY"]

        # Side walls collisions.
        if self.ball["x"] <= 0 or self.ball["x"] >= self.canvas["width"]:
            self.ball["speedX"] *= -1

        # Player1 paddle collision.
        if self.check_collision(self.ball, self.paddles['player1']):
            self.ball["y"] = self.paddles['player1']["y"] - self.ball["size"] / 2
            self.ball["speedY"] = -abs(self.ball["baseSpeed"] * self.paddles['player1']["speedModifier"])
            self.collision_count += 1

        # Player2 paddle collision
        elif self.check_collision(self.ball, self.paddles['player2']):
            self.ball["y"] = self.paddles['player2']["y"] + self.paddles['player2']["height"] + self.ball['size'] / 2
            self.ball["speedY"] = abs(self.ball["baseSpeed"] * self.paddles['player2']["speedModifier"])
            self.collision_count += 1

        # Player2 point
        if self.ball["y"] >= self.canvas["height"]:
            self.paddles['player2']["score"] += 1
            self.reset_ball()
        # Player1 point
        elif self.ball["y"] <= 0:
            self.paddles['player1']["score"] += 1
            self.reset_ball()

        # Generate power up.
        self.generate_power_up()
        return self.ball

    def check_collision(self, ball, paddle):
        """
        Check if the ball collide with a given paddle.

        :param ball: ball to check its collision.
        :param paddle: user paddle.

        :return: True when a collision is detected, False otherwise.
        """
        collision = (
                paddle["x"] < ball["x"] < paddle["x"] + paddle["width"] and
                ball["y"] + ball["size"] / 2 > paddle["y"] and
                ball["y"] - ball["size"] / 2 < paddle["y"] + paddle["height"]
        )
        if collision:
            hit_point = ball['x'] - (paddle['x'] + paddle['width'] / 2)
            normalized_hp = hit_point / (paddle['width'] / 2)
            self.ball['speedX'] = normalized_hp * 6
        return collision

    def generate_power_up(self):
        """
        Generate a random power up when collision threshold collision counter is
        reached, and append it to the power up list.
        """
        if self.collision_count >= self.collision_threshold and len(self.power_ups) == 0:
            from_player = random.random() > 0.5
            paddle_key = "player1" if from_player else "player2"
            paddle = self.paddles[paddle_key]

            direction_y = -3 if from_player else 3
            direction_x = (random.random() - 0.5) * 2
            types = ['>>', '<<']
            power_up_type = random.choice(types)

            self.power_ups.append({
                "x": paddle["x"] + paddle["width"] / 2 - self.power_up_size / 2,
                "y": paddle["y"],
                "startY": paddle["y"],
                "speedY": direction_y,
                "speedX": direction_x,
                "type": power_up_type,
                "active": False
            })
            logger.info("POWER UP")
            self.collision_count = 0

    def move_power_up(self):
        """
        Move the power up after its lunch.
        """
        for item in self.power_ups:
            item['y'] += item['speedY']
            item['x'] += item['speedX']

            if item['x'] + self.power_up_size > self.canvas['width'] or item['x'] < 0:
                item['speedX'] *= -1
            if item['y'] > self.canvas['height'] or item['y'] < 0:
                self.power_ups.remove(item)

    def apply_power_up(self, role, power_up_type):
        """
        Apply the power up to a given user role.
        A power up should affect paddle properties.

        :param role: paddle role (player1, player2).
        :param power_up_type: Power up behaviour.
        """
        player = self.paddles[role]
        if power_up_type == ">>":
            self.paddles[role]["width"] = min(player["width"] + 10, self.canvas["width"] - 45)
            self.paddles[role]["speedModifier"] = max(player["speedModifier"] - 0.1, 0.8)
        elif power_up_type == "<<":
            self.paddles[role]["width"] = max(player["width"] - 10, 50)
            self.paddles[role]["speedModifier"] = min(player["speedModifier"] + 0.1, 1.2)

    def check_power_up_collisions(self):
        """
        Check power up collision.
        Like a ball, the power up will be moving around the field, until it is catch,
        or get lost beyond the end of the field.
        """
        for item in self.power_ups:
            distance = abs(item["startY"] - item["y"])
            item["active"] = distance >= self.power_up_size

            if not item["active"]:
                continue
            # Power-up ball collision.
            if (
                    self.ball["x"] < item["x"] + self.power_up_size and
                    self.ball["x"] + self.ball["size"] > item["x"] and
                    self.ball["y"] < item["y"] + self.power_up_size and
                    self.ball["y"] + self.ball["size"] > item["y"]
            ):
                self.ball["speedY"] *= -1
                self.ball["speedX"] *= -1
                self.power_ups.remove(item)
                continue
            # Power-up captured by player1
            if (
                    item["x"] < self.paddles["player1"]["x"] + self.paddles["player1"]["width"] and
                    item["x"] + self.power_up_size > self.paddles["player1"]["x"] and
                    item["y"] < self.paddles["player1"]["y"] + self.paddles["player1"]["height"] and
                    item["y"] + self.power_up_size > self.paddles["player1"]["y"]
            ):
                self.apply_power_up("player1", item["type"])
                self.power_ups.remove(item)
                continue
            # Power-up captured by player2
            if (
                    item["x"] < self.paddles["player2"]["x"] + self.paddles["player2"]["width"] and
                    item["x"] + self.power_up_size > self.paddles["player2"]["x"] and
                    item["y"] < self.paddles["player2"]["y"] + self.paddles["player2"]["height"] and
                    item["y"] + self.power_up_size > self.paddles["player2"]["y"]
            ):
                self.apply_power_up("player2", item["type"])
                self.power_ups.remove(item)


    def update_paddle_position(self, role, position):
        """
        Update paddle position for a given role player.
        This method is called when an update message is received.

        :param role: player role
        :param position: new x position.
        """
        self.paddles[role]['x'] = position

    def update_game(self):
        """
        Update all the game (ball, power ups, and paddles).
        And return them to be sent using player instances.

        :return: paddles, power ups, ball.
        """
        self.update_ball_position()
        self.move_power_up()
        self.check_power_up_collisions()
        return self.paddles, self.power_ups, self.ball

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
                }))
                waiting_list.append(self)

        elif data.get("step") == "update":
            """
            Get update game from player, update paddle position and
            return game data updated
            """
            role = data.get("role")
            matches[self.match_id]['game'].update_paddle_position(role, data.get('position'))
            game_info = matches[self.match_id]
            paddles, power_ups, ball = game_info['game'].update_game()
            keys_to_remove = ["role", "y", "height"]
            for role in PLAYER_ROLES:
                opp = 'player1' if role == 'player2' else 'player2'
                player = {key: value for key, value in paddles[role].items() if key not in keys_to_remove}
                await game_info["players"][role].send(text_data=json.dumps({
                    "step": "update",
                    "playerRole": role,
                    "player": player,
                    "opponent": paddles[opp],
                    "ball": ball,
                    "powerUps": power_ups
                }))

    async def send_start_screen(self, game):
        """
        Send start game, to get user attention before the game is started.

        :param game: game instance.
        """
        logger.info('Send start screen messages', extra={"corr": self.match_id})
        await self.broadcast_message("Be prepare to fight!")
        await asyncio.sleep(3)
        await self.broadcast_message("2 seconds to go!")
        await asyncio.sleep(2)
        await self.broadcast_message("GO!", "go")
        await asyncio.sleep(0.5)
        logger.info('Prepare message sent.', extra={"corr": self.match_id})


    async def broadcast_message(self, message, step="ready"):
        """
        Broadcast a message to users involved at game.

        :param message: Detailed message to sent to each user.
        :param step: step sent
        """
        game_info = matches[self.match_id]
        paddles, power_ups, ball = game_info['game'].update_game()
        for role in PLAYER_ROLES:
            opp = 'player1' if role == 'player2' else 'player2'
            await game_info["players"][role].send(text_data=json.dumps({
                "step": step,
                "message": message,
                "playerRole": game_info["players"][role].player_role,
                "opponentName": game_info["players"][opp].username,
                "player1": paddles["player1"],
                "player2": paddles["player2"],
                "ball": ball
            }))


    async def disconnect(self, close_code):
        logger.warning(f"Client disconnected {close_code}")
        if (self.status == 'wait'):
            pass
        if self.player_id and self.player_id in self.players:
            del self.players[self.player_id]
            print(f"Jugador {self.player_id} eliminado del juego.")


class MatchAI(AsyncWebsocketConsumer):
    """
    Remote AI handler.
    A independent Remote AI instance, to keep remote websocket
    lighter.
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
        """
        A simple algorithm to play against.

        :param position: AI position (x).
        :param ball: Remote ball.
        """
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