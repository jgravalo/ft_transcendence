from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_translations, name='get_translations'),
]
