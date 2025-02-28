from django.db import models

# Create your models here.

from users.models import User

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"

class Group(models.Model):
    room = models.TextField()
    history = models.ManyToManyField(Message, symmetrical=False, related_name='message_for', blank=True)
