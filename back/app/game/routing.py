from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # re_path(r'ws/game/$', consumers.PongBack.as_asgi())
    re_path(r'ws/game/$', consumers.PongConsumer.as_asgi())
]
