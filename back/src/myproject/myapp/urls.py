from django.urls import path
from ..myapp2.views import my_view

urlpatterns = [
    path('api/my-endpoint/', my_view, name='my-endpoint'),
]