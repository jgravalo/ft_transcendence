from django.db import models

# Create your models here.
#class User(models.Model):
class User(models.Model):
	username = models.CharField(max_length=100)
	email = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	image = models.ImageField(upload_to='', default='España.webp') # Carpeta dentro de MEDIA_ROOT
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)
	matches = models.IntegerField(default=0)
	logged = models.BooleanField(default=False)
	two_fa_enabled = models.BooleanField(default=False)
	jwt = models.CharField(max_length=512, null=True, blank=True)
	friends = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
#
#	def __str__(self):
#       return self.username  # Representación amigable del objeto

	def num_friends(self):
		return self.friends.count()