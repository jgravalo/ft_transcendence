from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/game/$', consumers.Match.as_asgi()),
    re_path(r'ws/game/async/$', consumers.AsyncMatch.as_asgi()),
]