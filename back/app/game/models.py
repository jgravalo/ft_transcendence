from django.db import models
from django.db import models
from django.contrib.auth import get_user_model
from itertools import combinations
import uuid

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

class Tournament(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # Campo de UUID único.
	name = models.CharField(default=f'tournament_{self.id}')
	size = models.IntegerField(default=0)
	number = models.IntegerField(default=0)
	players = models.ManyToManyField(User, symmetrical=False, related_name='tournaments', blank=True)

	def add_player(self, user):
		self.players.add(user)
		self.size = self.players.count()
		if self.size == self.number:
			self.play()

	def play(self):
		start = Round.objects.create(
			tournament=self,
			name=self.name,
			number=self.number,
			size=self.size,
			)
		start.players.set(self.players.all())
		start.play()

class Round(models.Model):
	tournament = models.ForeignKey(Tournament, related_name='round_of', on_delete=models.CASCADE)
	size = models.IntegerField(default=0)
	number = models.IntegerField(default=0)
	players = models.ManyToManyField(User, symmetrical=False, related_name='tournaments', blank=True)
	matches = models.ManyToManyField(Match, symmetrical=False, related_name='matches_did', blank=True)	

	def add_player(self, user):
		self.players.add(user)
		self.size = self.players.count()
		if self.size == self.number:
			self.play()

	def play(self):
		players = list(self.players.all()) # Obtener todos los usuarios
		pairs = list(combinations(players, 2)) # Generar parejas únicas sin repetición
		if self.number > 2:
			next_round = self.objects.create(
				tournament=self.tournament,
				number=self.number / 2
				)

		# Mostrar las parejas
		for pair in pairs:
			print(pair[0].username, "-", pair[1].username)
			# room_name = f"game_to{uuid.uuid4().hex[:8]}"
			# pair[0].invite(pair[0], room_name)
			# pair[1].invite(pair[1], room_name)
			
			# for debug
			winner = random.choice(pair)
			if self.number == 2:
				self.tournament.winner = winner
			else:
				next_round.add_player(winner)