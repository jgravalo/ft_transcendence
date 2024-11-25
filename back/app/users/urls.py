from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('login/close/', views.close_login, name='close_login'),
    path('login/set/', views.set_login, name='set_login'),
    path('register/', views.register, name='register'),
]
