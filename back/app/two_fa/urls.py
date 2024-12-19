from django.urls import path
from . import views

urlpatterns = [
    path('two_fa/', views.two_fa, name='two_fa'),
    path('two_fa/email/', views.verify_otp, name='verify_otp'),
]