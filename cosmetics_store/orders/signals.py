from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderItem


def send_order_email(order):
    subject = f"🛒 New Order #{order.id}"
    message = (
        f"Customer: {order.user if order.user else 'Guest'}\n"
        f"Total price: ${order.total_amount:.2f}\n"
        f"Items:\n"
    )

    for item in order.items.all():
        message += f" - {item.product.name} x {item.quantity}\n"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.STORE_OWNER_EMAIL],
        fail_silently=False,
    )
    
@receiver(post_save, sender=OrderItem)
def update_order_total_and_notify(sender, instance, created, **kwargs):
    """Recalculate total when new OrderItem is added."""
    if created:
        order = instance.order
        total = sum(item.price * item.quantity for item in order.items.all())
        order.total_amount = total
        order.save(update_fields=["total_amount"])

        # Send email only after order is completed (for simplicity, when first created)
        if order.status == "pending":  # you can customize this later
            send_order_email(order)