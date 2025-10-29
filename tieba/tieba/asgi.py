"""
ASGI config for tieba project.
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tieba.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # WebSocket chat handler will be added later
})