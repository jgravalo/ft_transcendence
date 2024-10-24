from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('change/', views.change, name='change'),
    path('json/', views.json, name='json'),
]