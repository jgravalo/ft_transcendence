from django.db import models
from django.contrib.auth.models import AbstractUser
from .token import decode_token
import uuid

# Create your models here.

class User(AbstractUser):
# class User(models.Model):
# 	username = models.CharField(max_length=100)
# 	email = models.CharField(max_length=100)
	email = models.EmailField(max_length=100, unique=True)  # Asegura que el email sea único
# 	password = models.CharField(max_length=100)
#	is_active = models.BooleanField(default=True)
#	user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # Campo de UUID único.
	image = models.ImageField(upload_to='', default='default.jpg') # Carpeta dentro de MEDIA_ROOT
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)
	matches = models.IntegerField(default=0)
	two_fa_enabled = models.BooleanField(default=False)
	#history = models.ManyToManyField(Match, symmetrical=False, related_name='players', blank=True)
	friends = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
	blocked = models.ManyToManyField('self', symmetrical=False, related_name='blocked_by', blank=True)
	groups = models.ManyToManyField(
		"auth.Group",
		related_name="user_set",  # Evita el conflicto con 'auth.User.groups'
 		blank=True
    )
	user_permissions = models.ManyToManyField(
		"auth.Permission",
		related_name="user_permissions_set",  # Evita el conflicto con 'auth.User.user_permissions'
		blank=True
	)

	# USERNAME_FIELD = "username"
	# REQUIRED_FIELDS = []

	def __str__(self):
		return self.username  # Representación amigable del objeto

	@classmethod
	def get_user(cls, request):
		token = request.headers.get('Authorization').split(" ")[1]
		#if token == 'empty':
		data = decode_token(token)
		print("data =", data)
		return cls.objects.get(id=data["id"])

	def num_friends(self):
		return self.friends.count()