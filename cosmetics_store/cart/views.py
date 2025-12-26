from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from products.models import Product
from .serializers import CartSerializer, CartItemSerializer
from .utils import get_user_or_guest_cart


class CartView(generics.RetrieveAPIView):
    """Get the current user's or guest's cart"""
    serializer_class = CartSerializer

    def get_object(self):
        return get_user_or_guest_cart(self.request)


class AddToCartView(generics.GenericAPIView):
    """Add a product to the cart"""
    serializer_class = CartItemSerializer

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)
        if product.stock < quantity:
            return Response({"error": "Not enough stock available."}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_user_or_guest_cart(request)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpdateCartItemView(generics.GenericAPIView):
    """Update quantity of a cart item"""
    serializer_class = CartItemSerializer

    def patch(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        cart = get_user_or_guest_cart(request)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        if cart_item.product.stock < quantity:
            return Response({"error": "Not enough stock available."}, status=status.HTTP_400_BAD_REQUEST)
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RemoveFromCartView(generics.DestroyAPIView):
    """Remove a product from the cart"""

    def delete(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        cart = get_user_or_guest_cart(request)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        cart_item.delete()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
