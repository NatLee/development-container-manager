
from django.urls import re_path
from xterm import consumers

websocket_urlpatterns = [
    re_path(r"ws/console/$", consumers.ConsoleConsumer.as_asgi()),
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
