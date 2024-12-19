from django.urls import path
from . import views

urlpatterns = [
    path('two_fa/', views.verify_otp, name='verify_otp'),
]