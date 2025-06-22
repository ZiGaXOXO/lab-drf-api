from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('api/products/count/', consumers.ProductCountConsumer.as_asgi()),
]
