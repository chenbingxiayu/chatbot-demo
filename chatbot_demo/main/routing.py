from django.urls import path
from main.consumer import AssignmentConsumer

websocket_urlpatterns = [
    path('ws/notify_assignment/', AssignmentConsumer.as_asgi())
]
