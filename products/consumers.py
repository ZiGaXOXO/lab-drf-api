import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Product

class ProductCountConsumer(AsyncWebsocketConsumer):
    group_name = 'product_count_group'

    async def connect(self):
        # присоединяемся к группе
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        # При подключении сразу отправляем текущее количество доступных товаров
        count = await self.get_available_count()
        await self.send(text_data=json.dumps({'available_count': count}))

    async def disconnect(self, close_code):
        # убираемся из группы
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # метод для получения count в синхронном режиме через database_sync_to_async
    @database_sync_to_async
    def get_available_count(self):
        return Product.objects.filter(available=True).count()

    # метод, который будет вызван при событии "product_update"
    async def product_update(self, event):
        # event содержит новое количество
        count = event['available_count']
        await self.send(text_data=json.dumps({'available_count': count}))
