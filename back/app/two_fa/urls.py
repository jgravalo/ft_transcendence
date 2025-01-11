from django.urls import path
from . import views

urlpatterns = [
    path('', views.two_fa, name='two_fa'),
    path('verify/', views.verify, name='verify'),
    path('verify/set/', views.verify_otp, name='verify_otp'),
]