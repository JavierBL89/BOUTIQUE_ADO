# 2.POINT 2 OF THE LESSON CHECKOUT SIGNALS on the notebook
from django.db.models.signals import post_save, post_delete
# 3.POINT 3 OF THE LESSON CHECKOUT SIGNALS on the notebook
from django.dispatch import receiver
# 4.POINT 4 OF THE LESSON CHECKOUT SIGNALS on the notebook
from .models import OrderLineItem

# 6.POINT 6 OF THE LESSON CHECKOUT MODELS on the notebook
@receiver(post_save, sender=OrderLineItem)
# 5.POINT 5 OF THE LESSON CHECKOUT MODELS on the notebook
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    instance.order.update_total()

@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    instance.order.update_total()