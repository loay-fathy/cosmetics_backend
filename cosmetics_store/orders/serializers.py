from django.forms import ValidationError
from rest_framework import serializers
from .models import InstantCheckout, Order, OrderItem
from products.models import Product
from django.utils import timezone


class InstantCheckoutCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = InstantCheckout
        fields = ("product_id", "quantity")

    def validate(self, attrs):
        product_id = attrs.get("product_id")
        quantity = attrs.get("quantity", 1)
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product_id": "Product not found"})

        if product.stock < quantity:
            raise serializers.ValidationError({"quantity": "Insufficient stock"})

        attrs["product"] = product
        attrs["total_amount"] = product.price * quantity
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None
        session_key = None
        if request and not user:
            session_key = request.session.session_key or request.session.create()

        checkout = InstantCheckout.objects.create(
            user=user,
            session_key=session_key,
            product=validated_data["product"],
            quantity=validated_data.get("quantity", 1),
            total_amount=validated_data["total_amount"],
        )
        return checkout


class InstantCheckoutSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = InstantCheckout
        fields = ("id", "product", "quantity", "total_amount", "expires_at", "is_completed")

    def get_product(self, obj):
        return {"id": obj.product.id, "name": obj.product.name, "price": str(obj.product.price), 'main_image_url': obj.product.main_image.url if obj.product.main_image else None}


class OrderCreateSerializer(serializers.Serializer):
    """
    Handles the logic for creating an order, allowing users to
    use their profile address or provide a new one.
    """
    use_profile_address = serializers.BooleanField(default=False, write_only=True)
    
    # We set required=False here because they might be filled by the profile
    shipping_full_name = serializers.CharField(max_length=255, required=False)
    shipping_phone = serializers.CharField(max_length=20, required=False)
    shipping_governorate = serializers.CharField(max_length=100, required=False)
    shipping_city = serializers.CharField(max_length=100, required=False)
    shipping_address_detail = serializers.CharField(max_length=255, required=False)
    
    # For 'Buy Now' flow
    checkout_id = serializers.UUIDField(required=False, write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        use_profile = attrs.get('use_profile_address', False)

        if use_profile:
            if not user.is_authenticated:
                raise ValidationError("Guests cannot use profile address.")
            
            # Check if profile shipping info is complete
            profile_info = {
                'shipping_full_name': user.username,
                'shipping_phone': user.phone,
                'shipping_governorate': user.governorate,
                'shipping_city': user.city,
                'shipping_address_detail': user.address_detail,
            }
            
            # Check for missing profile data
            if not all(profile_info.values()) or not user.username:
                raise ValidationError({
                    "profile": "Your profile is incomplete. Please fill in your name, phone, and address."
                })
            
            # Use profile info
            attrs.update(profile_info)

        else:
            # Manual address entry. Check that all fields were provided.
            required_fields = [
                'shipping_full_name', 'shipping_phone', 
                'shipping_governorate', 'shipping_city', 'shipping_address_detail'
            ]
            missing = [field for field in required_fields if not attrs.get(field)]
            if missing:
                raise ValidationError({
                    field: "This field is required when not using profile address." for field in missing
                })
        
        return attrs

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("product", "name", "price", "quantity")


# --- MODIFIED SERIALIZER ---
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True) # Set read_only

    class Meta:
        model = Order
        # Add all the new shipping fields
        fields = (
            "id", "user", "session_key", "total_amount", "status", "created_at", "items",
            "shipping_full_name", "shipping_phone", "shipping_governorate",
            "shipping_city", "shipping_address_detail"
        )
        # These are set upon creation, not by direct user input to this serializer
        read_only_fields = (
            "id", "user", "session_key", "total_amount", "status", "created_at", "items",
            "shipping_full_name", "shipping_phone", "shipping_governorate",
            "shipping_city", "shipping_address_detail"
        )