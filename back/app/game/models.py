from django.db import models
from django.db import models
from django.contrib.auth import get_user_model
from itertools import combinations
from types import SimpleNamespace
import uuid
import random

# Create your models here.
# game/models.py

User = get_user_model()

class Match(models.Model):
	room = models.TextField()
	player1 = models.ForeignKey(User, related_name='match_player1', on_delete=models.CASCADE)
	player2 = models.ForeignKey(User, related_name='match_player2', on_delete=models.CASCADE)
	score_player1 = models.IntegerField(default=0)
	score_player2 = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.player1} vs {self.player2} - {self.score_player1}:{self.score_player2}"
	
	@property
	def winner(self):
		if self.score_player1 > self.score_player2:
			return self.player1
		elif self.score_player1 < self.score_player2:
			return self.player2
		return None
	
	@property
	def loser(self):
		if self.score_player1 < self.score_player2:
			return self.player1
		elif self.score_player1 > self.score_player2:
			return self.player2
		return None


class Tournament(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # Campo de UUID único.
	name = models.CharField(default=f'tournament_{uuid.uuid4}', max_length=255, blank=True)
	size = models.IntegerField(default=0)
	number = models.IntegerField(default=0)
	players = models.ManyToManyField(User, symmetrical=False, related_name='tournaments', blank=True)
	winner = models.ForeignKey(User, null=True, related_name='trophies', on_delete=models.CASCADE)

	@property
	def is_full(self):
		return self.size == self.number

	def add_player(self, user):
		if self.is_full:
			return
		self.players.add(user)
		self.size = self.players.count()
		self.save()
		# if self.size == self.number:
		if self.is_full:
			# self.is_full = True
			self.play()
			
	def remove_player(self, user):
		if self.is_full:
			return False  # Can't leave if tournament is full/started
		if user in self.players.all():
			self.players.remove(user)
			self.size = self.players.count()
			self.save()
			return True
		return False

	def play(self):
		start = Round.objects.create(
			tournament=self,
			number=self.number,
			size=self.size,
			)
		start.players.set(self.players.all())
		start.play()

class Round(models.Model):
	tournament = models.ForeignKey(Tournament, related_name='round_of', on_delete=models.CASCADE)
	size = models.IntegerField(default=0)
	number = models.IntegerField(default=0)
	players = models.ManyToManyField(User, symmetrical=False, related_name='rounds', blank=True)
	matches = models.ManyToManyField(Match, symmetrical=False, related_name='matches_did', blank=True)	

	@property
	def is_full(self):
		return self.size == self.number

	def add_player(self, user):
		if self.is_full:
			return
		self.players.add(user)
		self.size = self.players.count()
		print(f'space: {self.size}/{self.number}')
		if self.is_full:
		# if self.size == self.number:
			self.play()

	def play(self):
		# pairs = list(combinations(players, 2)) # Generar parejas únicas sin repetición
		players = list(self.players.all()) # Obtener todos los usuarios
		pairs = [] # Generar parejas únicas sin repetición
		for i in range(0, len(players), 2):
			# print(f'round of {self.number}:')
			pairs.append(players[i:i+2])
		if self.number > 2:
			next_round = Round.objects.create(
				tournament=self.tournament,
				number=self.number / 2
				)
		# Mostrar las parejas
		for pair in pairs:
			print(pair[0].username, "-", pair[1].username)

			# real

			info = SimpleNamespace(round=self.number, tournament=self.tournament.id)
			room_name = f"game_to{uuid.uuid4().hex[:8]}"
			print(f'room_name: {room_name}: {pair[0].username} vs {pair[1].username}')

			pair[0].invite(pair[0], room_name, info)
			pair[1].invite(pair[1], room_name, info)
			
			""" # for debug
			winner = random.choice(pair)
			if self.number == 2:
				print(f'winner: {winner}')
				self.tournament.winner = winner
			else:
				next_round.add_player(winner) """