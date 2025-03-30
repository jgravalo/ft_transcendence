import threading
import time

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

from channels.generic.websocket import AsyncWebsocketConsumer
import random
import math
import logging
import sys
from app.logging_config import get_logger

import json
import asyncio
import uuid
from asgiref.sync import sync_to_async
from django.apps import apps
from channels.generic.websocket import AsyncWebsocketConsumer


logger = get_logger("app-logger")

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
from channels.db import database_sync_to_async


@database_sync_to_async
def create_match_and_update_users(player1, player2, score1, score2):
    logger.debug("create_match_and_update_users")
    from game.models import Match
    Match = apps.get_model('game', 'Match')
    # game = await sync_to_async(Match.objects.create)(
    #     player1=player1,
    #     player2=player2,
    #     score_player1=score1,
    #     score_player2=score2
    # )

    # match = Match.objects.create(
    #     player1=player1,
    #     player2=player2,
    #     score_player1=score1,
    #     score_player2=score2
    # )
    if score1 > score2:
        player1.wins += 1
        player2.losses += 1
    elif score2 > score1:
        player2.wins += 1
        player1.losses += 1

    player1.matches += 1
    player2.matches += 1

    player1.save()
    player2.save()

    return match


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


class Tournaments:
    def __init__(self, participants):
        self.clients_mutex = threading.Lock()
        self.participants = participants
        self.matches = []
        self.winners = []
        self.loosers = []
        self.clients = []
        self.cardex = {}
        self.spare = []

    def create_tournament(self):
        """
        Create a cardex to save all the matches and avoid repeated matches.
        """
        for client in self.clients:
            self.cardex[client.cnn_id] = []

    def create_round(self):
        """
        Create a round of matches.
        """
        pairs = self.create_pairs()
        if self.spare:
            logger_to_client(self.spare[0], "You are the spare player.")
        for pair in pairs:
            pair["player1"].module = pair["player1"].module = game = GameSession(pair)
            game.send_start_screen()

    def create_pairs(self):
        """
        Create a set of matches for a given round.
        """
        players = self.clients.copy()
        self.spare = []
        # Shuffle players
        random.shuffle(players)
        used = []
        pairs = []
        spare = []
        round = []
        for i, client in enumerate(players):
            if client in used:
                continue
            candidates = []
            for other in clients[i + 1:]:
                if (other not in used) and (other not in self.cardex[client.cnn_id]):
                    candidates.append(other)
            if candidates:
                players = {}
                partner = random.choice(candidates)
                pairs.append(client, partner)
                role = f"player{str(random.randint(1, 2))}"
                players = {
                    role: client,
                    "player1" if role == "player2" else "player2": partner
                }
                round.append(players)
                used.add(client)
                used.add(partner)
            else:
                spare.append(client)

        return pairs

    async def join_tournament(self, client):
        with self.clients_mutex:
            self.clients.append(client)
        await logger_to_client(client, "You are in the tournament.")

    async def leave_tournament(self, client):
        with self.clients_mutex:
            self.clients.remove(client)
        await logger_to_client(client, "You are out of the tournament.")


class Clients:
    """
    Class to control all users connected to app
    """
    clients = []
    challenges = []

    def __init__(self):
        self.clients_mutex = threading.Lock()
        self.challenges_mutex = threading.Lock()

    def get_client(self, client_id):
        """
        Get a client instance by id.
        :param client_id: Client id.
        :return: Instance of client, None if not found.
        """
        found = None
        with self.clients_mutex:
            for client in self.clients:
                if client.cnn_id == client_id:
                    found = client
                    break
        return found

    async def clean_for_waiting(self, client):
        """
        Clean the waiting list.
        This method iterates over each client waiting list and remove
        the client instance.

        :param client: Client instance to remove.
        """
        with self.clients_mutex:
            for clt in self.clients:
                clt.update_challengers(client, False)


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

    async def append_random_challenge(self, challenger, message="Random challenge created."):
        """
        Append a random challenge.

        :param challenger: Client instance.
        """
        with self.challenges_mutex:
            if challenger not in self.challenges:
                self.challenges.append(challenger)
                await logger_to_client(challenger, message)
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
        logger.info(f"get_opponent {challenger} - {opponent_username}")
        with self.challenges_mutex:
            if self.challenges and challenger not in self.challenges:
                if opponent_username:
                    found = None
                    for i, obj in enumerate(self.challenges, 0):
                        if obj.cnn_id == opponent_username:
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
        for client in self.clients:
            connected = msg
            my_cnn = {"id": client.cnn_id, "username": client.username}
            if my_cnn in connected:
                connected.remove(my_cnn)
            await client.send(text_data=json.dumps({
                "payload_update": "connected-users",
                "detail": connected
            }))

    async def broadcast_challenges(self):
        """
        Broadcast to all users an update of available challenges.
        """
        with self.clients_mutex:
            msg = [{"id": clt.cnn_id, "username": clt.username} for clt in self.challenges]
        for client in self.clients:
            my_challenge = {"id": client.cnn_id, "username": client.username}
            challenges = msg
            if my_challenge in challenges:
                challenges.remove(my_challenge)
            await client.send(text_data=json.dumps({
                "payload_update": "challenges-update",
                "detail": challenges
            }))

ClientsHandler = Clients()

class GameSession:
    """
    Game Session class to control and update the game with a asyncio loop.
    """
    roles = ['player1', 'player2']
    keys_to_remove = ["role", "y", "height"]

    # --- Collisions and power ups
    collision_threshold = 2  # Cada cuántas colisiones se genera un power-up
    base_ball = {
        'speedX': 200.0,
        'speedY': 200.0,
        'baseSpeed': 200.0
    }
    game_mutex = threading.Lock()
    def __init__(self, players, tournament=False, width=400, height=800):
        """
        :param players: dict con 'player1' y 'player2' (sus conexiones).
        :param width: ancho del canvas
        :param height: alto del canvas
        """
        self.canvas = {'width': width, 'height': height}
        self.players = players
        self.match_id = str(uuid.uuid4())

        logger.info(f"New game: {self.match_id} | Player1: {self.players['player1']} | Player2: {self.players['player2']}", extra={"corr": self.match_id})

        # -- Ball
        self.ball = {
            'x': width / 2,
            'y': height / 2,
            'size': 15,
            'speedX': self.base_ball['speedX'],
            'speedY': self.base_ball['speedY'],
            'baseSpeed': self.base_ball['baseSpeed'],
        }

        # Power-ups
        self.power_ups = []
        self.power_up_size = self.ball['size'] * 1.5
        self.power_up_act_dist = self.power_up_size * 3

        # Counters
        self.collision_count = 0
        self.collision_to_points = 0

        # Paddles
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

        # Control Game
        self.running = True
        self.starting = False
        self.winner = None
        self.rematch = False

        # Time between updates
        self.last_update = time.time()

        # Global Matches Registry
        matches[self.match_id] = self

        # Main loop
        self._game_loop_task = asyncio.create_task(self.game_loop())

    def waiting_rematch(self):
        """
        Waiting for rematch.
        """
        self.rematch = True

    def rematch_accepted(self):
        return self.rematch

    def game_players(self):
        """
        Return the players of the game.

        :return: self.players dict.
        """
        return self.players

    async def game_loop(self):
        """
        Main game loop.

        This loop ensures the game runs at a constant frame rate.
        """
        fps = 60
        interval = 1.0 / fps
        await self.send_start_screen()
        self.last_update = time.time()  
        while self.running:
            now = time.time()
            delta = now - self.last_update
            self.last_update = now
            self.update_game(delta)
            if self.winner:
                self.running = False
                await self.end_game()
                break
            await self.broadcast_state()
            await asyncio.sleep(interval)
        logger.info(f"Game loop finished. Match ID: {self.match_id}", extra={"corr": self.match_id})
        logger.info(f"{self.players['player1'].logged} and {self.players['player2'].logged}")
        if self.players['player1'].logged and self.players['player2'].logged:
            create_match_and_update_users(self.players['player1'].username,
                                          self.players['player2'].username,
                                          self.paddles['player1']['score'],
                                          self.paddles['player2']['score'])

    def update_game(self, delta):
        """
        Update game state.
        :param delta: delta time between updates.
        """

        self.update_ball_position(delta)
        self.move_power_up(delta)
        self.check_power_up_collisions()

        if self.paddles['player1']['score'] == 5 or self.paddles['player2']['score'] == 5:
            self.winner = 'player1' if self.paddles['player1']['score'] == 5 else 'player2'

    def update_ball_position(self, delta):
        """
        Move the ball and check for collisions.

        :param delta: time between updates.
        """
        # Update ball position
        self.ball["x"] += self.ball["speedX"] * delta
        self.ball["y"] += self.ball["speedY"] * delta

        # Side walls: ball bounces
        if self.ball["x"] <= 0:
            self.ball["x"] = 0
            self.ball["speedX"] *= -1
            self.collision_to_points += 1
        elif self.ball["x"] >= self.canvas["width"]:
            self.ball["x"] = self.canvas["width"]
            self.ball["speedX"] *= -1
            self.collision_to_points += 1

        # Player1 paddle: ball bounces
        if self.check_collision(self.ball, self.paddles['player1']):
            self.ball["y"] = self.paddles['player1']["y"] - (self.ball["size"] / 2)
            self.ball["speedY"] = -abs(self.ball["baseSpeed"] * self.paddles['player1']["speedModifier"])
            self.collision_count += 1

            # Side Paddles: modify ball position
            hit_point = self.ball['x'] - (self.paddles['player1']['x'] + self.paddles['player1']['width'] / 2)
            normalized_hp = hit_point / (self.paddles['player1']['width'] / 2)
            self.ball['speedX'] = normalized_hp * 6 * (self.paddles['player1']["speedModifier"] * 50)

        # Player2 paddle: ball bounces
        elif self.check_collision(self.ball, self.paddles['player2']):
            self.ball["y"] = self.paddles['player2']["y"] + self.paddles['player2']["height"] + (self.ball['size'] / 2)
            self.ball["speedY"] = abs(self.ball["baseSpeed"] * self.paddles['player2']["speedModifier"])
            self.collision_count += 1
            self.collision_to_points += 1

            # Side Paddles: modify ball position
            hit_point = self.ball['x'] - (self.paddles['player2']['x'] + self.paddles['player2']['width'] / 2)
            normalized_hp = hit_point / (self.paddles['player2']['width'] / 2)
            self.ball['speedX'] = normalized_hp * 6 * (self.paddles['player2']["speedModifier"] * 50)

        # Point for player2
        if self.ball["y"] >= self.canvas["height"]:
            self.paddles['player2']["score"] += 1
            self.paddles['player2']['points'] += int(self.collision_to_points * (100 / self.paddles['player2']['width']))
            self.collision_to_points = 0
            self.reset_ball()

        # Point for player1
        elif self.ball["y"] <= 0:
            self.paddles['player1']["score"] += 1
            self.paddles['player1']['points'] += int(self.collision_to_points * (100 / self.paddles['player1']['width']))
            self.collision_to_points = 0
            self.reset_ball()

        # Generate power-up
        self.generate_power_up()

    def check_collision(self, ball, paddle):
        """
        Collision detection between ball and paddle.

        :param ball: ball dict
        :param paddle: paddle dict
        """
        collision = (
            paddle["x"] < ball["x"] < (paddle["x"] + paddle["width"]) and
            (ball["y"] + (ball["size"] / 2)) > paddle["y"] and
            (ball["y"] - (ball["size"] / 2)) < (paddle["y"] + paddle["height"])
        )
        return collision

    def reset_ball(self):
        """
        Reset ball position and speed.
        """
        self.ball.update(self.base_ball)
        self.ball["x"] = self.canvas['width'] / 2
        self.ball["y"] = self.canvas['height'] / 2

        angle = (random.random() - 0.5) * (math.pi / 4)
        # Random direction (left or right)
        self.ball["speedX"] = self.ball["baseSpeed"] * math.sin(angle)
        # Random direction (up or down)
        self.ball["speedY"] = self.ball["baseSpeed"] * math.cos(angle) * (1 if random.random() > 0.5 else -1)

        self.collision_count = 0

    def generate_power_up(self):
        """
        Generates a power-up if collision_count >= collision_threshold and currentl
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
            self.collision_count = 0

    def move_power_up(self, delta):
        """
        Move power-ups and check for collisions.

        :param delta: time between updates.
        """
        to_remove = []
        for item in self.power_ups:
            item['y'] += item['speedY'] * 50 * delta
            item['x'] += item['speedX'] * 50 * delta

            # Side walls collision
            if item['x'] + self.power_up_size > self.canvas['width'] or item['x'] < 0:
                item['speedX'] *= -1

            # Power-up out of bounds
            if item['y'] > self.canvas['height'] or item['y'] < 0:
                to_remove.append(item)

        for item in to_remove:
            self.power_ups.remove(item)

    def check_power_up_collisions(self):
        """
        Check for power-up collisions with paddles and ball.
        """
        to_remove = []
        for item in self.power_ups:
            distance = abs(item["startY"] - item["y"])
            item["active"] = distance >= self.power_up_size

            if not item["active"]:
                continue

            # Power-up collision with ball
            if (
                (self.ball["x"] < item["x"] + self.power_up_size) and
                (self.ball["x"] + self.ball["size"] > item["x"]) and
                (self.ball["y"] < item["y"] + self.power_up_size) and
                (self.ball["y"] + self.ball["size"] > item["y"])
            ):
                # Power-up collision with ball
                self.ball["speedY"] *= -1
                self.ball["speedX"] *= -1
                to_remove.append(item)
                continue

            # Power-up captured by player1
            if (
                item["x"] < (self.paddles["player1"]["x"] + self.paddles["player1"]["width"]) and
                (item["x"] + self.power_up_size) > self.paddles["player1"]["x"] and
                item["y"] < (self.paddles["player1"]["y"] + self.paddles["player1"]["height"]) and
                (item["y"] + self.power_up_size) > self.paddles["player1"]["y"]
            ):
                self.apply_power_up("player1", item["type"])
                to_remove.append(item)
                continue

            # Power-up captured by player2
            if (
                item["x"] < (self.paddles["player2"]["x"] + self.paddles["player2"]["width"]) and
                (item["x"] + self.power_up_size) > self.paddles["player2"]["x"] and
                item["y"] < (self.paddles["player2"]["y"] + self.paddles["player2"]["height"]) and
                (item["y"] + self.power_up_size) > self.paddles["player2"]["y"]
            ):
                self.apply_power_up("player2", item["type"])
                to_remove.append(item)

        for item in to_remove:
            self.power_ups.remove(item)

    def apply_power_up(self, role, power_up_type):
        """
        Applies the power-up to the player.

        :param role: player role
        :param power_up_type: power-up type
        """
        player = self.paddles[role]
        if power_up_type == ">>":
            # Increase width and reduce speed
            player["width"] = min(player["width"] + 10, self.canvas["width"] - 45)
            player["speedModifier"] = max(player["speedModifier"] - 0.1, 0.8)
        elif power_up_type == "<<":
            # Reduce width and increase speed
            player["width"] = max(player["width"] - 10, 50)
            player["speedModifier"] = min(player["speedModifier"] + 0.1, 1.2)
        player['points'] += 10

    def update_paddle_position(self, role, position):
        """
        Update the paddle position.

        :param role: player role
        :param position: new position
        """
        self.paddles[role]['x'] = position

    async def receive(self, data):
        """
        Process received message.

        :param data: json object received.
        """
        if data.get("step") == "update":
            # Update paddle position
            role = data.get("role")
            new_pos = data.get("position")
            self.update_paddle_position(role, new_pos)

    async def broadcast_state(self):
        """
        Send the game state to both players.
        """

        if not self.running:
            return

        for role, user in self.players.items():
            opp = 'player1' if role == 'player2' else 'player2'
            player_data = {k: v for k, v in self.paddles[role].items() if k not in self.keys_to_remove}
            try:
                await user.send(text_data=json.dumps({
                    "step": "update",
                    "id": self.match_id,
                    "score1": self.paddles['player1']['score'],
                    "score2": self.paddles['player2']['score'],
                    "playerRole": role,
                    "player": player_data,
                    "opponent": self.paddles[opp],
                    "ball": self.ball,
                    "powerUps": self.power_ups
                }))
            except Exception as e:
                logger.warning(f"Error sending update to {role}.\n{str(e)}", extra={"corr": self.match_id})

    async def send_start_screen(self):
        """
        Send a start screen to both players.
        """
        logger.info(f"Sends start screen messages. Match ID: {self.match_id}", extra={"corr": self.match_id})
        await self.broadcast_log()
        await self.broadcast_message("Be prepared to fight!")
        await asyncio.sleep(3)
        await self.broadcast_message("3 seconds to go!")
        await asyncio.sleep(2)
        await self.broadcast_message("Go!", "go")
        await asyncio.sleep(1)


    async def broadcast_log(self):
        """
        Broadcast a log message to both players.
        """
        msg = f"New game {self.players['player1'].username} vs {self.players['player2'].username}."
        for role, user in self.players.items():
            await logger_to_client(user, msg)

    async def broadcast_message(self, message, step="ready"):
        """
        Broadcast a message to both players.
        This method is used to send start messages only.

        :param message: message to send.
        :param step: step to send.
        """
        for role, user in self.players.items():
            opp = 'player1' if role == 'player2' else 'player2'
            try:
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
            except Exception as e:
                logger.warning(f"Error sending start message to {role}.\n{str(e)}", extra={"corr": self.match_id})
                # TODO abort game.

    async def broadcast_payload(self, update, detail):
        """
        Broadcast a payload message to both players.

        :param update: payload update to send.
        :param detail: payload detail to send.
        """
        with self.game_mutex:
            for role, user in self.players.items():
                try:
                    await user.send(text_data=json.dumps({
                        "payload_update": update,
                        "detail": detail
                    }))
                except Exception as e:
                    logger.warning(f"Error sending start message to {role}.\n{str(e)}", extra={"corr": self.match_id})


    async def end_game(self):
        """
        End the game and send the result to both players.
        """
        for role, user in self.players.items():
            if role == self.winner:
                msg = f"You Won {self.paddles[role]['points']} points."
            else:
                msg = "You lost..."
            try:
                await user.send(text_data=json.dumps({
                    "step": "endOfGame",
                    "id": self.match_id,
                    "winner": self.winner,
                    "message": msg
                }))
                await logger_to_client(user, msg)
            except Exception as e:
                logger.error(f"Error sending end message to {role}.\n{str(e)}", extra={"corr": self.match_id})


    async def disconnect_game(self):
        """
        Send a disconnect message to both players.
        """
        # TODO send aborting message
        for role, user in self.players.items():
            try:
                await user.send(text_data=json.dumps({
                    "step": "disconnect",
                    "id": self.match_id
                }))
            except Exception as e:
                logger.warning(f"Error sending disconnect message to {role}.\n{str(e)}", extra={"corr": self.match_id})

    async def rematch_reject(self):
        """
        Rematch is rejected by one of the players.
        """
        for role, user in self.players.items():
            await user.send(text_data=json.dumps({
                "step": "end",
                "id": self.match_id
            }))

    async def end_game_db(self):
        """
        (Opcional) Guarda info de la partida en BD.
        """
        user1 = self.players["player1"].scope["user"]
        user2 = self.players["player2"].scope["user"]

        score1 = self.paddles["player1"]["score"]
        score2 = self.paddles["player2"]["score"]

        # await create_match_and_update_users(user1, user2, score1, score2)

class PongBack(AsyncWebsocketConsumer):
    cnn_id = None
    username = None
    logged = False
    module = None
    modes = ["remote", "remote-ai"]
    challengers = []
    challenger_mutex = threading.Lock()
    # free = True
    async def connect(self):
        self.cnn_id = str(uuid.uuid4())
        try:
            await self.accept()
            user = self.scope['user'] # IMPORTANTE
            logger.info(f"Connected to {self.scope['user']}")
            if user.is_authenticated: # redundante, self.scope['user'] solo va si is_authenticated
                self.username = user.username # self.scope['user']
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
        await ClientsHandler.broadcast_connected_users()



    async def receive(self, text_data):
        """
        Process received message.

        :param self: connection instance.
        :param text_data: json object received.
        """
        data = json.loads(text_data)
        # Join to remote mode
        if not "step" in data:
            # -- Error control
            logger.error(f"Connection {self.cnn_id} wrong request data: {data}.", extra={"corr": self.cnn_id})
            await logger_to_client(self, f"Error. Wrong request.")
            await self.close(code=4001)
        if data.get("step") == "end":
            # -- End Game
            if data.get("mode") == "remote-ai":
                msg = "Yo beat HAL!" if data.get("score1") > data.get("score1") else "Hal Crushed you!"
                await logger_to_client(self, msg)
                del self.module
            self.module = None
        if data.get("step") == "reject_my_challenge":
            # -- Reject personal challenge
            logger.info(f"User reject personal challenge.", extra={"corr": self.cnn_id})
            opponent = ClientsHandler.get_client(data.get("challenge_id"))
            if opponent:
                await ClientsHandler.clean_for_waiting(opponent)
                opponent.send(text_data=json.dumps({
                    "step": "end"
                }))
                await self.update_challengers(opponent, False)
                await logger_to_client(opponent, f"{self.username} rejected your challenge.")
        if data.get("step") == "join":
            # -- Join to a game: Join to a game
            if data.get("mode") == "remote-ai":
                self.module = MatchHAL(self)
                await logger_to_client(self, f"You are ready to play with HAL!")
            if data.get("mode") == "remote":
                # -- Create or play a random challenge
                await self.build_game()
            if data.get("mode") == "create_challenge":
                #  -- Create a challenge
                if self.logged:
                    await self.send(text_data=json.dumps({
                        "step": "wait",
                        "playerName": self.username
                    }))
                    await ClientsHandler.append_random_challenge(self, "Remote challenge created.")
                else:
                    await self.send(text_data=json.dumps({
                        "step": "end"
                    }))
                    await logger_to_client(self, "You must be logged to create a challenge.")
            if data.get("mode") == "challenge-user":
                # -- Challenge a user
                if "info" not in data:
                    await logger_to_client(self, "Error challenging an user.")
                    await self.send(text_data=json.dumps({
                        "step": "end"
                    }))
                    return
                opponent = ClientsHandler.get_client(data.get("info"))
                logger.info(data)
                if not opponent:
                    await logger_to_client(self, "Opponent was not found. :-(")
                    await self.send(text_data=json.dumps({
                        "step": "end"
                    }))
                    return
                await self.send(text_data=json.dumps({
                    "step": "wait",
                    "playerName": self.username
                }))
                await opponent.update_challengers(self)
                await logger_to_client(self, f"Your challenge was sent to {opponent.username}.")
            if data.get("mode") == "accept_challenge":
                # -- Accept random challenge
                logger.info(f"User accept random challenge.", extra={"corr": self.cnn_id})
                await self.build_game(data.get("info"))
            if data.get("mode") == "accept_my_challenge":
                # -- Accept personal challenge
                logger.info(f"User accept personal challenge.", extra={"corr": self.cnn_id})
                opponent = ClientsHandler.get_client(data.get("info"))
                logger.info(f"opponent {opponent}")
                if not opponent:
                    await logger_to_client(self, f"Challenge is not longer available.")
                    await self.send(text_data=json.dumps({
                        "step": "end"
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        "step": "wait",
                        "playerName": self.username
                    }))
                    await self.build_game(opponent_instance=opponent)
        if data.get("step") == "rematch":
            # -- Rematch request
            logger.info(f"Rematch request from {self.username}", extra={"corr": self.cnn_id})
            if not self.module:
                logger.error(f"There is no module to cancel.", extra={"corr": self.cnn_id})
            else:
                if self.module.rematch_accepted():
                    await self.build_rematch()
                else:
                    self.module.waiting_rematch()
                    players = self.module.game_players()
                    for role, player in players.items():
                        if player != self:
                            await logger_to_client(player, f"{self.username} wants a rematch.")
                    await self.module.broadcast_payload("rematch", "Rematch Accepted.")
        if data.get("step") == "rematch-cancel":
            # -- Cancel rematch
            if not self.module:
                logger.error(f"There is no module to cancel.", extra={"corr": self.cnn_id})
            else:
                await self.module.broadcast_payload("rematch-cancel", "Rematch canceled.")
        if data.get("step") == "game-cancel":
            # -- Cancel game
            if not self.module:
                logger.error(f"There is no module to cancel.", extra={"corr": self.cnn_id})
            else:
                try:
                    del matches[self.module.match_id]
                except Exception as e:
                    logger.warning(f"Error deleting matches {self.module.match_id}.\n{str(e)}",)
        if data.get("game-abort"):
            # -- Abort game
            if not self.module:
                logger.error(f"There is no module to cancel.", extra={"corr": self.cnn_id})
            else:
                await self.module.broadcast_payload("game-abort", "Game aborted.")
        if data.get("step") == "abort-waiting":
            # -- Abort waiting
            logger.info(f"User remove challenges.", extra={"corr": self.cnn_id})
            await ClientsHandler.remove_random_challenge(self)
            await ClientsHandler.clean_for_waiting(self)
        # if data.get("step") == "accept_my_challenge":
        #     # -- Accept personal challenge
        #     logger.info(f"User accept personal challenge.", extra={"corr": self.cnn_id})
        #     opponent = ClientsHandler.get_client(data.get("challenge_id"))
        #     logger.info(f"opponent {opponent}")
        #     if not opponent:
        #         await logger_to_client(self, f"Challenge is not longer available.")
        #         await self.send(text_data=json.dumps({
        #             "step": "end"
        #         }))
        #     else:
        #         await self.send(text_data=json.dumps({
        #             "step": "wait",
        #             "playerName": self.username
        #         }))
        #         await self.build_game(opponent_instance=opponent)

        else:
            if self.module:
                await self.module.receive(data)

    async def update_challengers(self, challenger, append_challenge=True):
        with self.challenger_mutex:
            if append_challenge is True:
                self.challengers.append(challenger)
                await logger_to_client(self, f"{challenger.username} challenges you!.")
            else:
                if challenger in self.challengers:
                    self.challengers.remove(challenger)
        challenges = [{"id": clt.cnn_id, "username": clt.username} for clt in self.challengers]
        await self.send(text_data=json.dumps({
            "payload_update": "my-challenges",
            "detail": challenges
        }))


    async def build_rematch(self):
        players = self.module.game_players()
        for role, player in players.items():
            if player != self:
                await self.build_game(opponent_instance=player)

    async def build_game(self, challenger=None, opponent_instance=None):
        logger.info(f"{challenger} - {opponent_instance}")
        opponent = ClientsHandler.get_opponent(self, challenger) if not opponent_instance else opponent_instance
        if opponent:
            logger.info("Join remote game request.", extra={"corr": self.cnn_id})
            logger.info(f"Players waiting to play: {len(waiting_list)}", extra={"corr": self.cnn_id})
            # Get Opponent to the match.
            role = f"player{str(random.randint(1, 2))}"
            players = {
                role: self,
                "player1" if role == "player2" else "player2": opponent
            }
            self.module = opponent.module = GameSession(players)
        else:
            await self.send(text_data=json.dumps({
                "step": "wait",
                "playerName": self.username
            }))
            await ClientsHandler.append_random_challenge(self)


    async def disconnect(self, close_code):
        logger.warning(f"Client disconnected {close_code}", extra={"corr": self.cnn_id})
        ClientsHandler.clean_for_waiting(self)
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
        self.last_update = time.time()
        self._game_loop_task = asyncio.create_task(self.game_loop())

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
    # self._game_loop_task = asyncio.create_task(self.game_loop())
    async def game_loop(self):
        """
        Main game loop.

        This loop ensures the game runs at a constant frame rate.
        """
        fps = 60
        interval = 1.0 / fps
        await self.send_start_screen()
        self.last_update = time.time()
        while self.running:
            await self.ws.send(text_data=json.dumps({
                "step": "move",
                "id": self.match_id,
                "position": self.position
            }))
            await asyncio.sleep(interval)
        logger.info(f"AI Game loop finished. Match ID: {self.match_id}", extra={"corr": self.match_id})

