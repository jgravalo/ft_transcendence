import asyncio
import threading
import json
import uuid
import time
from cgitb import reset
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

from channels.generic.websocket import AsyncWebsocketConsumer
import random
import math
import logging
import json
import sys
from app.logging_config import get_logger

logger = get_logger("game-back")  # Puedes cambiar el nombre según el módulo

waiting_list = []
client_list = []
playing_list = []
matches = {}
rematch = {}

CANVAS = {'width': 400, 'height': 800}
PLAYER_ROLES = ['player1', 'player2']
MUTEX = asyncio.Lock()
WAITING_MUTEX = threading.Lock()
CHALLENGE_MUTEX = threading.Lock()
CLIENT_MUTEX = threading.Lock()

# ----
# from channels.db import database_sync_to_async
# from app.game.models import Match
#
# @database_sync_to_async
# def create_match_and_update_users(player1, player2, score1, score2):
#     match = Match.objects.create(
#         player1=player1,
#         player2=player2,
#         score_player1=score1,
#         score_player2=score2
#     )
#     if score1 > score2:
#         player1.wins += 1
#         player2.losses += 1
#     elif score2 > score1:
#         player2.wins += 1
#         player1.losses += 1
#
#     player1.matches += 1
#     player2.matches += 1
#
#     player1.save()
#     player2.save()
#
#     return match
# ----



async def logger_to_client(client, message, update_detail="log-update"):
    """
    Send a message to log section.

    :param client: instance of client to send a message.
    :param message: message to send.
    :param update_detail: update detail to send.
    """
    try:
        await client.send(text_data=json.dumps({
            "payload_update": update_detail,
            "detail": message
        }))
        logger.info(f"Log message sent. {update_detail} - {message}.", extra={"corr": client.cnn_id})
    except Exception as e:
        logger.warning(f"Error sending log update message.{e} {message}", extra={"corr": client.cnn_id})

class Clients:
    """
    Class to control all users connected to app
    """
    clients = []
    challenges = []

    def __init__(self):
        self.clients_mutex = threading.Lock()
        self.challenges_mutex = threading.Lock()

    async def append_client(self, client):
        """
        Append client instance to control all the environment.

        :param client: client instance
        """
        with self.clients_mutex:
            if client not in self.clients:
                self.clients.append(client)
        await self.broadcast_connected_users()

    def delete_client(self, client):
        """
        Delete a client instance from clients control.

        :param client: client instance.
        """
        with self.clients_mutex:
            if client in self.clients:
                self.clients.remove(client)
        self.broadcast_connected_users()

    async def append_random_challenge(self, challenger):
        """
        Append a random challenge.

        :param challenger: Client instance.
        """
        with self.challenges_mutex:
            if challenger not in self.challenges:
                self.challenges.append(challenger)
                await logger_to_client(challenger, "Random challenge created.")
            else:
                return
        await self.broadcast_challenges()

    async def remove_random_challenge(self, challenger):
        """
        Delete a random challenge.

        :param challenger: Client instance to remove.
        """
        with self.challenges_mutex:
            if challenger in self.challenges:
                self.challenges.remove(challenger)
                await logger_to_client(challenger, "Your random challenge was deleted.")
            else:
                return
        await self.broadcast_challenges()

    def get_opponent(self, challenger, opponent_username=None):
        """
        Get a random opponent (first from the list).

        :param challenger: Client instance to avoid double challenges.
        :param opponent_username: opponent ID to get a specific opponent.
        """
        with self.challenges_mutex:
            if len(self.challenges) and challenger not in self.challenges:
                if opponent_username:
                    found = None
                    for i, obj in enumerate(self.challenges):
                        if obj.username == opponent_username:
                            found = self.challenges.pop(i)
                            break
                    if not found:
                        logger_to_client(challenger, "Random challenge does not exist.")
                        logger.warning("Error getting challenge.", extra={"corr": challenger.cnn_id})
                    return found
                opponent = self.challenges.pop(0)
            else:
                return None
        self.broadcast_challenges()
        return opponent

    async def broadcast_connected_users(self):
        """
        Broadcast to all users an update of connected users.
        """
        with self.clients_mutex:
            msg = [{"id": clt.cnn_id, "username": clt.username} for clt in self.clients]
        msg = msg if len(msg) else "empty"
        for client in self.clients:
            await client.send(text_data=json.dumps({
                "payload_update": "connected-users",
                "detail": msg
            }))

    async def broadcast_challenges(self):
        """
        Broadcast to all users an update of available challenges.
        """
        if not len(self.challenges):
            return
        with self.clients_mutex:
            msg = [{"id": clt.cnn_id, "username": clt.username} for clt in self.challenges]
        msg = msg if len(msg) else "empty"
        for client in self.clients:
            await client.send(text_data=json.dumps({
                "payload_update": "challenges-update",
                "detail": msg
            }))

ClientsHandler = Clients()


class GameSession:
    """
    Game Session class to control and update the game.
    """
    roles = ['player1', 'player2']
    keys_to_remove = ["role", "y", "height"]
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
    base_ball = {
        'speedX': float(4),
        'speedY': float(4),
        'baseSpeed': float(4)
    }
    winner = None
    running = True
    starting = False
    def __init__(self, players, width=400, height=800):
        """
        Init method to GameSession class

        :param players: a list of the players involved.
        :param width: canvas width. Optional.
        :param height: canvas height. Optional.
        """
        self.canvas = {'width': width, 'height': height}
        # Assign randomly roles to players.
        for key, value in players.items():
            self.users[key] = value
        self.players = players
        self.match_id = str(uuid.uuid4())
        logger.info(f"New game was created {self.match_id}. Player1 {self.players['player1']} | Player2 {self.players['player2']}.", extra={"corr": self.match_id})
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
        matches[self.match_id] = self
        # self.send_start_screen()


    async def receive(self, data):
        """
        Process received message.

        :param self: connection instance.
        :param text_data: json object received.
        """
        # Join to remote mode
        if data.get("step") == "update":
            """
            Get update game from player, update paddle position and
            return game data updated
            """
            role = data.get("role")
            self.update_paddle_position(role, data.get('position'))
            await self.send_update_status()

    async def end_game(self):
        for role, user in self.players.items():
            msg = f"You won {self.paddles[role]['points']} points!" if role == self.winner else "You lost!"
            try:
                await user.send(text_data=json.dumps({
                    "step": "endOfGame",
                    "id": self.match_id,
                    "winner": self.winner,
                    "message": msg
                }))
            except Exception as e:
                logger.warning(f"Error sending end status to {role}.", extra={"corr": self.match_id})

    async def disconnect_game(self):
        for role, user in self.players.items():
            try:
                await user.send(text_data=json.dumps({
                    "step": "disconnect",
                    "id": self.match_id
                }))
            except Exception as e:
                logger.warning(f"Error sending disconnect message to {role}.", extra={"corr": self.match_id})

    async def send_update_status(self):
        """
        Get update game from player, update paddle position and
        return game data updated
        """
        if not self.running:
            return
        self.update_game()
        if self.winner:
            self.running = False
            await self.end_game()
        for role, user in self.players.items() :
            opp = 'player1' if role == 'player2' else 'player2'
            player = {key: value for key, value in self.paddles[role].items() if key not in self.keys_to_remove}
            await user.send(text_data=json.dumps({
                "step": "update",
                "id": self.match_id,
                "score1": self.paddles['player1']['score'],
                "score2": self.paddles['player2']['score'],
                "playerRole": role,
                "player": player,
                "opponent": self.paddles[opp],
                "ball": self.ball,
                "powerUps": self.power_ups
            }))

    async def send_start_screen(self):
        """
        Send start game, to get user attention before the game is started.

        :param game: game instance.
        """
        logger.info('Send start screen messages', extra={"corr": self.match_id})
        await self.broadcast_log()
        await self.broadcast_message("Be prepare to fight!")
        await asyncio.sleep(3)
        await self.broadcast_message("3 seconds to go!")
        await asyncio.sleep(2)
        await self.broadcast_message("Go!", "go")
        await asyncio.sleep(1)
        self.running = True
        await self.send_update_status()
        logger.info('Prepare message sent.', extra={"corr": self.match_id})

    async def broadcast_log(self):
        """
        Broadcast logger message to users involved at game.
        """
        for role, user in self.players.items() :
            await logger_to_client(user,
                                   f"New game {self.players['player1'].username} - {self.players['player2'].username}.")

    async def broadcast_message(self, message, step="ready"):
        """
        Broadcast a message to users involved at game.

        :param message: Detailed message to sent to each user.
        :param step: step sent
        """
        for role, user in self.players.items() :
            opp = 'player1' if role == 'player2' else 'player2'
            await user.send(text_data=json.dumps({
                "step": step,
                "id": self.match_id,
                "message": message,
                "playerRole": role,
                "playerName": self.players[role].username,
                "opponentName": self.players[opp].username,
                "player1Name": self.players['player1'].username,
                "player2Name": self.players['player2'].username,
                "player1": self.paddles["player1"],
                "player2": self.paddles["player2"],
                "ball": self.ball
            }))

    async def rematch_reject(self):
        for role, user in self.players.items() :
            await user.send(text_data=json.dumps({
                "step": "end",
                "id": self.match_id
            }))

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
        self.ball.update(self.base_ball)
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
            self.collision_to_points += 1

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
            self.collision_to_points += 1

        # Player2 point
        if self.ball["y"] >= self.canvas["height"]:
            self.paddles['player2']["score"] += 1
            self.paddles['player2']['points'] += int(self.collision_to_points * (100 / self.paddles['player2']['width']))
            self.collision_to_points = 0
            self.reset_ball()
        # Player1 point
        elif self.ball["y"] <= 0:
            self.paddles['player1']["score"] += 1
            self.paddles['player1']['points'] += int(self.collision_to_points * (100 / self.paddles['player1']['width']))
            self.reset_ball()
            self.collision_to_points = 0

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
        self.paddles[role]['points'] += 10

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
        if not self.starting:
            self.reset_ball()
            self.starting = True
        self.update_ball_position()
        self.move_power_up()
        self.check_power_up_collisions()
        if self.paddles['player1']['score'] == 5 or self.paddles['player2']['score'] == 5:
            self.winner = 'player1' if self.paddles['player1']['score'] == 5 else 'player2'

    async def end_game_db(self):
        user1 = self.players["player1"].scope["user"]
        user2 = self.players["player2"].scope["user"]

        score1 = self.paddles["player1"]["score"]
        score2 = self.paddles["player2"]["score"]

        # Llamar a la función que crea el Match y actualiza estadísticas
        await create_match_and_update_users(user1, user2, score1, score2)


class PongBack(AsyncWebsocketConsumer):
    cnn_id = None
    username = None
    logged = False
    module = None
    modes = ["remote", "remote-ai"]
    # free = True
    async def connect(self):
        self.cnn_id = str(uuid.uuid4())
        try:
            await self.accept()
            user = self.scope['user']
            if user.is_authenticated:
                self.username = user.username
                self.logged = True
                logger.info(f'Logged user connected: conn {self.cnn_id} - user {self.username}',
                            extra={"corr": self.cnn_id})
            else:
                random_number = str(random.randint(1, 999)).zfill(3)
                self.username = f'shy_guy-{random_number}'
                logger.info(f'Anonymous user connected: conn {self.cnn_id} - user {self.username}',
                            extra={"corr": self.cnn_id})
        except Exception as e:
            logger.error(f'Connection Error {self.cnn_id} - Detail {e}',
                         extra={"corr": self.cnn_id})
            return
        await logger_to_client(self, f"You are connected as {self.username}")
        await ClientsHandler.append_client(self)



    async def receive(self, text_data):
        """
        Process received message.

        :param self: connection instance.
        :param text_data: json object received.
        """
        data = json.loads(text_data)
        # Join to remote mode
        if not "step" in data:
            logger.error(f"Connection {self.cnn_id} wrong request data: {data}.", extra={"corr": self.cnn_id})
            await logger_to_client(self, f"Error. Wrong request.")
            await self.close(code=4001)
        if data.get("step") == "end":
            if data.get("mode") == "remote-ai":
                msg = "Yo beat HAL!" if data.get("score1") > data.get("score1") else "Hal Crushed you!"
                await logger_to_client(self, msg)
                del self.module
            self.module = None
        if data.get("step") == "join":
            if data.get("mode") == "remote-ai":
                self.module = MatchHAL(self)
                await logger_to_client(self, f"You are ready to play with HAL!")
                await self.module.receive(data)
                # await self.module.game_loop()
            if data.get("mode") == "remote":
                await self.build_game(data)
        if data.get("step") == "handshake":
            await self.send(text_data=json.dumps({
                "step": "handshake"
            }))
        if data.get("step") == "rematch-cancel":
            logger.info("LLegamos aqui...")
            if not self.module or data.get("id") != self.module.match_id:
                logger.info(f'?? {data.get("id")} {self.module.match_id}')
                pass
            else:
                self.module.rematch_reject()
                logger.error(f"User rejects rematch {self.module.match_id}", extra={"corr": self.cnn_id})
            pass
        if data.get("step") == "abort-waiting":
            logger.info(f"User remove random challenge.", extra={"corr": self.cnn_id})
            await ClientsHandler.remove_random_challenge(self)
        if data.get("step") == "accept_challenge":
            await self.build_game(data.get("challenge_id"))
            logger.info(f"User accept random challenge.", extra={"corr": self.cnn_id})
        else:
            if self.module:
                await self.module.receive(data)

    async def build_game(self, challenger=None):
        opponent = ClientsHandler.get_opponent(self, challenger)
        if opponent:
            logger.info(type(opponent))
            logger.info(opponent)
            logger.info("Join remote game request.", extra={"corr": self.cnn_id})
            logger.info(f"Players waiting to play: {len(waiting_list)}", extra={"corr": self.cnn_id})
            # Get Opponent to the match.
            role = f"player{str(random.randint(1, 2))}"
            players = {
                role: self,
                "player1" if role == "player2" else "player2": opponent
            }
            self.module = opponent.module = GameSession(players)
            await self.module.send_start_screen()
        else:
            await self.send(text_data=json.dumps({
                "step": "wait",
                "playerName": self.username
            }))
            await ClientsHandler.append_random_challenge(self)
        pass

    async def disconnect(self, close_code):
        logger.warning(f"Client disconnected {close_code}", extra={"corr": self.cnn_id})
        ClientsHandler.delete_client(self)
        logger.info(f"Client removed from client list.", extra={"corr": self.cnn_id})
        if self.module:
            self.module.disconnect_game()
            logger.info(f"User disconnected from game.", extra={"corr": self.cnn_id})
        await ClientsHandler.remove_random_challenge(self)
        logger.info(f"User removed from waiting list.", extra={"corr": self.cnn_id})
        logger.info(f"User disconnection managed.", extra={"corr": self.cnn_id})


class MatchHAL:
    """
    Remote AI handler.
    A independent Remote AI instance, to keep remote websocket
    lighter.
    """
    position = 0
    running = True
    build_data = None
    def __init__(self, ws):
        self.ws = ws
        self.username = self.ws.username
        self.cnn_id = ws.cnn_id
        self.match_id = str(uuid.uuid4())
        self.position = CANVAS['width'] / 2
        # self.build_data = data

    async def receive(self, data):
        """
        Process received message.

        :param self: connection instance.
        :param data: parsed json object received.
        """

        if data.get("step") == "join":
            logger.info(f"Join AI game request.", extra={"corr": self.cnn_id})
            await self.ws.send(text_data=json.dumps({
                "step": "start",
                "id": self.match_id,
                "playerName": self.username,
                "opponentName": 'HAL-42',
            }))
            logger.info(f"Response remote-ai request. Start.", extra={"corr": self.cnn_id})
            # await self.opponent_ia(data)
        elif data.get("step") == "move":
            await self.opponent_ia(data.get("opponent"), data.get("ball"))

    async def disconnect_game(self):
        pass

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
        self.position = position['x']
        await self.ws.send(text_data=json.dumps({
            "step": "move",
            "id": self.match_id,
            "position": self.position
        }))

    async def game_loop(self):
        while self.running:
            await self.ws.send(text_data=json.dumps({
                "step": "move",
                "id": self.match_id,
                "position": self.position
            }))
            await asyncio.sleep(0.1)

class MatchControl:
    ws = None
    match_id = None
    cnn_id = None
    players = {}
    def __init__(self, ws):
        self.ws = ws
        self.cnn_id = self.ws.cnn_id

    async def receive(self, data):
        """
        Process received message.

        :param self: connection instance.
        :param text_data: json object received.
        """
        # Join to remote mode
        if data.get("step") == "join":
            logger.info("Join remote game request.", extra={"corr": self.cnn_id})
            logger.info(f"Players waiting to play: {len(waiting_list)}", extra={"corr": self.cnn_id})
            if waiting_list and self.ws not in waiting_list:
                async with MUTEX:
                    logger.info(f"Players Waiting. Create a new game.", extra={"corr": self.cnn_id})
                    # Get Opponent to the match.
                    opponent = waiting_list.pop(0)
                    role = f"player{str(random.randint(1, 2))}"
                    players = {
                        role: self.ws,
                        "player1" if role == "player2" else "player2": opponent.ws
                    }
                    self.players = players
                    await self.playball(players, opponent)
            else:
                await self.send(text_data=json.dumps({
                    "step": "wait",
                    "playerName": self.username
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
            paddles, power_ups, ball, winner = game_info['game'].update_game()
            if winner:
                logger.info("llego un ganador..")
                await self.end_game_winner(paddles, winner)
            keys_to_remove = ["role", "y", "height"]
            for role in PLAYER_ROLES:
                opp = 'player1' if role == 'player2' else 'player2'
                player = {key: value for key, value in paddles[role].items() if key not in keys_to_remove}
                await game_info["players"][role].send(text_data=json.dumps({
                    "step": "update",
                    "score1": paddles['player1']['score'],
                    "score2": paddles['player2']['score'],
                    "playerRole": role,
                    "player": player,
                    "opponent": paddles[opp],
                    "ball": ball,
                    "powerUps": power_ups
                }))

    async def playball(self, players, opponent):
        self.opponent = opponent
        self.match_id = str(uuid.uuid4())
        self.opponent.match_id = self.match_id
        self.opponent.opponent = self
        game = GameSession(self.match_id, players)
        logger.info(f"Match Created.", extra={"corr": self.match_id})
        logger.info(f"Players {self.username} - {self.opponent.username}", extra={"corr": self.match_id})
        self.player_role = game.get_role(self)
        self.opponent.player_role = game.get_role(self.opponent)
        logger.info(f'Random roles assigned', extra={"corr": self.match_id})
        matches[self.match_id] = {
            "players": players,
            "game": game
        }
        await self.send_start_screen(game)