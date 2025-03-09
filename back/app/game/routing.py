from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/game/$', consumers.Match.as_asgi()),
    re_path(r'ws/gamehal/$', consumers.MatchAI.as_asgi()),
    re_path(f'ws/challenges/$', consumers.Challenges.as_asgi())
]
