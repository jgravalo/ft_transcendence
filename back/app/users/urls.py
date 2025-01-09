from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('login/close/', views.close_login, name='close_login'),
    path('login/set/', views.set_login, name='set_login'),
    path('register/', views.register, name='register'),
    path('register/set/', views.set_register, name='set_register'),
    path('logout/', views.logout, name='logout'),
    path('logout/close/', views.close_logout, name='close_logout'),
    path('profile/', views.profile, name='profile'),
    path('update/', views.update, name='update'),
    path('update/set/', views.set_update, name='set_update'),
]
