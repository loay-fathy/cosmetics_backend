from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from cart.models import Cart
from .models import InstantCheckout, Order, OrderItem
from .serializers import (
    InstantCheckoutCreateSerializer,
    InstantCheckoutSerializer,
    OrderCreateSerializer,
    OrderSerializer,
)
from products.models import Product


class CreateInstantCheckoutView(generics.CreateAPIView):
    serializer_class = InstantCheckoutCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        checkout = serializer.save()
        return Response({"checkout_id": checkout.id}, status=status.HTTP_201_CREATED)


class InstantCheckoutDetailView(generics.RetrieveAPIView):
    queryset = InstantCheckout.objects.all()
    serializer_class = InstantCheckoutSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        checkout = self.get_object()
        if checkout.expires_at < timezone.now():
            return Response({"detail": "Checkout expired"}, status=status.HTTP_400_BAD_REQUEST)
        return super().get(request, *args, **kwargs)

class PlaceOrderView(generics.GenericAPIView):
    # --- MODIFIED ---
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # --- MODIFIED ---
        # Validate shipping info AND checkout_id
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        shipping_data = serializer.validated_data
        
        checkout_id = shipping_data.get("checkout_id")
        if not checkout_id:
            return Response({"checkout_id": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

        checkout = get_object_or_404(InstantCheckout, id=checkout_id, is_completed=False)

        if checkout.expires_at < timezone.now():
            return Response({"detail": "Checkout expired"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            product = Product.objects.select_for_update().get(id=checkout.product.id)
            if product.stock < checkout.quantity:
                return Response({"detail": "Insufficient stock"}, status=status.HTTP_400_BAD_REQUEST)

            product.stock -= checkout.quantity
            product.save()

            # --- MODIFIED: Add shipping data to the Order ---
            order = Order.objects.create(
                user=checkout.user,
                session_key=checkout.session_key,
                total_amount=checkout.total_amount,
                status="pending",
                shipping_full_name=shipping_data['shipping_full_name'],
                shipping_phone=shipping_data['shipping_phone'],
                shipping_governorate=shipping_data['shipping_governorate'],
                shipping_city=shipping_data['shipping_city'],
                shipping_address_detail=shipping_data['shipping_address_detail'],
            )
            # -------------------------------------------------

            OrderItem.objects.create(
                order=order,
                product=product,
                name=product.name,
                price=product.price,
                quantity=checkout.quantity,
            )

            checkout.is_completed = True
            checkout.save()

        # Use the display serializer for the response
        display_serializer = OrderSerializer(order)
        return Response(display_serializer.data, status=status.HTTP_201_CREATED)


class CreateOrderFromCartView(generics.GenericAPIView):
    # --- MODIFIED ---
    serializer_class = OrderCreateSerializer

    def post(self, request, *args, **kwargs):
        # --- MODIFIED ---
        # Validate shipping info
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        shipping_data = serializer.validated_data

        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key

        if user:
            cart = Cart.objects.filter(user=user).prefetch_related("items__product").first()
        else:
            cart = Cart.objects.filter(session_id=session_key).prefetch_related("items__product").first()

        if not cart or not cart.items.exists():
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # --- MODIFIED: Add shipping data to the Order ---
            order = Order.objects.create(
                user=user,
                session_key=session_key if not user else None,
                total_amount=0, # Will be calculated below
                status="pending",
                shipping_full_name=shipping_data['shipping_full_name'],
                shipping_phone=shipping_data['shipping_phone'],
                shipping_governorate=shipping_data['shipping_governorate'],
                shipping_city=shipping_data['shipping_city'],
                shipping_address_detail=shipping_data['shipping_address_detail'],
            )
            # -------------------------------------------------

            total = 0
            for item in cart.items.select_related("product").select_for_update():
                product = item.product
                if item.quantity > product.stock:
                    # Note: This will roll back the transaction
                    raise ValueError(f"Insufficient stock for {product.name}")

                subtotal = product.price * item.quantity
                total += subtotal

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    name=product.name, # Store a snapshot of the name
                    quantity=item.quantity,
                    price=product.price, # Store a snapshot of the price
                )

                product.stock -= item.quantity
                product.save()

            order.total_amount = total
            order.save()

            cart.items.all().delete()
            # You might want to delete the parent Cart object too
            # cart.delete()

        # Use the display serializer for the response
        display_serializer = OrderSerializer(order)
        return Response(display_serializer.data, status=status.HTTP_201_CREATED)