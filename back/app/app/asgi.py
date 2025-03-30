"""
ASGI config for app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from .token_auth_middleware import TokenAuthMiddleware
import game.routing
import users.routing
import chat.routing

application = get_asgi_application()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
        URLRouter(
            game.routing.websocket_urlpatterns +
            users.routing.websocket_urlpatterns +
            chat.routing.websocket_urlpatterns
        )
    ),
})