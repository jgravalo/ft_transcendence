from django.db import models
from users.models import User
import uuid

# Create your models here.

# game/models.py
from django.db import models
from django.contrib.auth import get_user_model

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
