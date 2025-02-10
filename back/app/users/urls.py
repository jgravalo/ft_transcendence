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
    path('delete/', views.delete_user, name='delete_user'),
    path('friends/', views.friends, name='friends'),
    path('friends/add/', views.add_friend, name='add_friend'),
    path('friends/delete/', views.delete_friend, name='delete_friend'),
    path('friends/block/', views.block_user, name='block_user'),
    path('friends/unlock/', views.unlock_user, name='unlock_user'),
    path('refresh/', views.refresh, name='refresh'),
    path('auth/42/login/', views.fortytwo_auth, name='fortytwo-login'),
    path('auth/42/callback/', views.fortytwo_callback, name='fortytwo_callback'),
]
