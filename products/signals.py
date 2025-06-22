from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer



@receiver([post_save, post_delete], sender=Product)
def product_change_handler(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    # Считаем текущее кол-во доступных
    count = Product.objects.filter(available=True).count()
    async_to_sync(channel_layer.group_send)(
        "product_count_group",
        {
            'type': 'product_update',
            'available_count': count
        }
    )
