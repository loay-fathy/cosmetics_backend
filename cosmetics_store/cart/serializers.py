from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product


class ProductSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight product serializer for cart use only.
    Keeps payload small and prevents circular imports.
    """
    
    main_image_url = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'main_image_url']  # include only essential info

    def get_main_image_url(self, obj):
        """Return the URL of the main image."""
        return obj.main_image.url if obj.main_image else None


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for individual cart items.
    Includes product details and total price per item.
    """
    product = ProductSummarySerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price']

    def get_total_price(self, obj):
        """Compute price * quantity safely."""
        return round(obj.product.price * obj.quantity, 2) if obj.product else 0


class CartSerializer(serializers.ModelSerializer):
    """
    Full cart serializer.
    Includes all items, computed total price, and avoids unnecessary nesting.
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'created_at']

    def get_total_price(self, obj):
        """Calculate total for all items efficiently."""
        return round(sum(item.product.price * item.quantity for item in obj.items.all()), 2)
