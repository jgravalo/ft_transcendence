from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('close_login/', views.close_login, name='close_login'),
    path('set_login/', views.set_login, name='set_login'),
    path('sign_up/', views.sign_up, name='sign_up'),
]
