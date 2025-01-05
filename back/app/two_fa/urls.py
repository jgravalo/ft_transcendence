from django.urls import path
from . import views

urlpatterns = [
    path('', views.two_fa, name='two_fa'),
    path('email/', views.email, name='email'),
    path('verify/', views.verify_otp, name='verify_otp'),
]