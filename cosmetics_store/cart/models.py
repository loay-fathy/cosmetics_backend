# cart/models.py
from django.db import models
from django.conf import settings
from decimal import Decimal

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             null=True, blank=True, db_index=True)
    session_id = models.CharField(max_length=255, null=True, blank=True, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart(User={self.user})" if self.user else f"Cart(Guest={self.session_id})"

    @property
    def total_price(self):
        total = Decimal('0.00')
        for item in self.items.select_related('product').all():
            total += item.total_price
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    @property
    def total_price(self):
        return self.product.price * self.quantity
