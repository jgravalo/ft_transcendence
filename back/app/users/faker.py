import os
import django
import random
from faker import Faker
from random import randint
from game.models import Match
from .models import User

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_proyecto.settings')
django.setup()

fake = Faker()

def create_fake_matches(n=1):
    for _ in range(n):
        users = list(User.objects.all())
        if users:
            player1 = random.choice(users)
            player2 = random.choice(users)
        while player1 == player2:  # Evitar que sean el mismo equipo
            player2 = random.choice(users)
        score1 = randint(0, 5)
        score2 = randint(0, 5)
        date = fake.date_time_this_year()

        match = Match.objects.create(player1=player1, player2=player2, score1=score1, score2=score2, date=date)
        print(f'Match creado: {match}')

# Generar 10 partidos aleatorios
# create_fake_matches(10)

def create_fake_users(n=1):
    for _ in range(n):
        username = fake.user_name()
        email = fake.email()
        password = "0987654321" # Puedes cambiarlo o hacer que sea aleatorio
        
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, email=email, password=password)
            print(f'Usuario creado: {user.username} - {user.email}')
        else:
            print(f'El usuario {username} ya existe.')

# Cambia el número de usuarios que quieres generar
# create_fake_users(10)

