from django.db import models
from users.models import User
import uuid

# Create your models here.

class Match(models.Model):
    id_match = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # Campo de UUID único.
    player1 = models.ForeignKey(User, related_name="matches_as_player1", on_delete=models.CASCADE)
    player2 = models.ForeignKey(User, related_name="matches_as_player2", on_delete=models.CASCADE)
    winner = models.ForeignKey(User, related_name="matches_won", on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    score1 = models.IntegerField(default=0)
    score2 = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.player1.username} vs {self.player2.username} - Winner: {self.winner.username if self.winner else 'N/A'}"
