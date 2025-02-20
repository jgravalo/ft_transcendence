from django.urls import re_path
from .consumers import PrivateChatConsumer

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<other_user_id>\d+)/$', PrivateChatConsumer.as_asgi()),
]
