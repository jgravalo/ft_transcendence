from django.db import models

# Create your models here.
class User(models.Model):
	username = models.CharField(max_length=100)
	email = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	logged = models.BooleanField(default=False)
	jwt = models.CharField(max_length=500)
#
#	def __str__(self):
#       return self.username  # Representación amigable del objeto