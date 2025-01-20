from django.db import models
from .token import decode_token
import uuid

# Create your models here.
class User(models.Model):
	user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # Campo de UUID único.
	username = models.CharField(max_length=100)
	email = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	image = models.ImageField(upload_to='', default='España.webp') # Carpeta dentro de MEDIA_ROOT
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)
	matches = models.IntegerField(default=0)
	logged = models.BooleanField(default=False)
	two_fa_enabled = models.BooleanField(default=True)
	jwt = models.CharField(max_length=512, null=True, blank=True)
	friends = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
#
#	def __str__(self):
#       return self.username  # Representación amigable del objeto

	@classmethod
	def get_user(cls, request):
		token = request.headers.get('Authorization').split(" ")[1]
		#if token == 'empty':
		data = decode_token(token)
		return cls.objects.get(user_id=data["user_id"])

	def num_friends(self):
		return self.friends.count()