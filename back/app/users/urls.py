from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.get_login, name='get_login'),
    path('login/close/', views.close_login, name='close_login'),
    path('login/set/', views.set_login, name='set_login'),
    path('register/', views.get_register, name='get_register'),
    path('register/set/', views.set_register, name='set_register'),
    path('logout/', views.get_logout, name='get_logout'),
    path('logout/close/', views.close_logout, name='close_logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/foreign/', views.foreign_profile, name='foreign_profile'),
    path('update/', views.update, name='update'),
    path('update/set/', views.set_update, name='set_update'),
    path('delete/', views.delete_user, name='delete_user'),
    path('friends/', views.friends, name='friends'),
    path('friends/edit/', views.edit_friend, name='edit_friend'),
    # path('friends/add/', views.add_friend, name='add_friend'),
    # path('friends/delete/', views.delete_friend, name='delete_friend'),
    # path('friends/block/', views.block_user, name='block_user'),
    # path('friends/unlock/', views.unlock_user, name='unlock_user'),
    path('refresh/', views.refresh, name='refresh'),
    path('auth/42/login/', views.fortytwo_auth, name='fortytwo-login'),
    path('auth/42/callback/', views.fortytwo_callback, name='fortytwo_callback'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
]
