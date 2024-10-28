from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'game/sock/$', consumers.Match.as_asgi()),
]