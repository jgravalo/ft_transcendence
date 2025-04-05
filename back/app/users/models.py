from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.contrib.sessions.models import Session


import uuid

# Create your models here.

class User(AbstractUser):
# class User(models.Model):
# 	username = models.CharField(max_length=100)
# 	email = models.CharField(max_length=100)
	email = models.EmailField(max_length=100, unique=True)  # Asegura que el email sea único
# 	password = models.CharField(max_length=100)
	is_online = models.BooleanField(default=True)
#	user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # Campo de UUID único.
	image = models.ImageField(upload_to='', default='default.jpg') # Carpeta dentro de MEDIA_ROOT
	image_42_url = models.URLField(max_length=255, blank=True, null=True)  # Campo para almacenar la URL de la imagen de 42
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)
	matches = models.IntegerField(default=0)
	points = models.IntegerField(default=0)
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
	# More secure way to get the user :)
	def get_user(cls, request):
		try:
			auth_header = request.headers.get('Authorization')
			if not auth_header:
				return None
			
			token = auth_header.split(" ")[1]
			# print("token =", token)
			# token = auth_header.split(" ")[0]
			if not token:
				return None
			

			try:
				token_obj = AccessToken(token)
				user_id = token_obj['user_id']
			except TokenError:
				return None
			
			try:
				user = cls.objects.get(id=user_id)
				return user
			except cls.DoesNotExist:
				return None
		
		except Exception:
			return None

	def num_friends(self):
		return self.friends.count()

	def delete(self, *args, **kwargs):
		# Limpiar relaciones
		self.friends.clear()
		self.blocked.clear()
		self.groups.clear()
		self.user_permissions.clear()
		
		# Eliminar imagen si no es la default
		if self.image and self.image.name != 'default.jpg':
			try:
				self.image.delete(save=False)
			except Exception as e:
				print(f"Error al eliminar imagen: {str(e)}")
		
		# Eliminar tokens JWT
		try:
			OutstandingToken.objects.filter(user=self).delete()
		except Exception as e:
			print(f"Error al eliminar tokens: {str(e)}")
		
		# Eliminar sesiones
		Session.objects.filter(session_data__contains=str(self.id)).delete()
		
		# Eliminar completamente el usuario y todos sus datos
		super().delete(*args, **kwargs)