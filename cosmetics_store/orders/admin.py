from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')
    can_delete = False
    show_change_link = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user_display',
        'total_amount',
        'status',
        'created_at',
        'updated_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username', 'user__email', 'session_key')
    readonly_fields = (
        'user',
        'session_key',
        'total_amount',
        'status',
        'created_at',
        'updated_at',
    )
    inlines = [OrderItemInline]
    ordering = ('-created_at',)

    def user_display(self, obj):
        """Display username if available, otherwise mark as guest."""
        return obj.user.username if obj.user else f"Guest ({obj.session_key[:8]})"
    user_display.short_description = "User"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')
    readonly_fields = ('order', 'product', 'quantity', 'price')
    list_filter = ('order__status',)
    ordering = ('-order__created_at',)
