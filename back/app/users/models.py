from django.db import models

# Create your models here.
class User(models.Model):
	username = models.CharField(max_length=100)
	email = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	image = models.ImageField(upload_to='')  # Carpeta dentro de MEDIA_ROOT
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)
	matches = models.IntegerField(default=0)
	logged = models.BooleanField(default=False)
	jwt = models.CharField(max_length=512, null=True, blank=True)
#
#	def __str__(self):
#       return self.username  # Representación amigable del objeto