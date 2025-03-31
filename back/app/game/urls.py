from django.urls import path
from . import views

urlpatterns = [
    path('', views.game, name='game'),
    path('local/', views.local_game, name='local_game'),
    path('remote/', views.remote_game, name='remote_game'),
]
