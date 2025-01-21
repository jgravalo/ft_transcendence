from django.urls import path
from . import views

urlpatterns = [
    path('', views.two_fa, name='two_fa'),
    path('phone/', views.phone, name='phone'),
    path('phone/set/', views.set_phone, name='set_phone'),
    path('verify/', views.verify, name='verify'),
    path('verify/set/', views.verify_otp, name='verify_otp'),
]