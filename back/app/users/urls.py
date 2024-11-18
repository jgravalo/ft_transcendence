from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    #path('set_login/', views.set_login, name='set_login'),
    path('sign_up/', views.sign_up, name='sign_up'),
]
