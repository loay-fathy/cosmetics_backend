from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'user__username', 'total_price', 'created_at')
    inlines = [CartItemInline]
    search_fields = ('user__username',)
