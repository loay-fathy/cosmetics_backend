# cart/utils.py
from django.db import transaction
from .models import Cart, CartItem

def merge_guest_cart_into_user(user, session_id):
    """
    Merge guest cart (session_id) into the user's cart atomically.
    If items overlap, sum quantities. Remove guest cart afterwards.
    """
    if not session_id:
        return

    try:
        guest_cart = Cart.objects.prefetch_related('items__product').get(session_id=session_id)
    except Cart.DoesNotExist:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)

    with transaction.atomic():
        for item in guest_cart.items.all():
            user_item, created = CartItem.objects.get_or_create(
                cart=user_cart, product=item.product,
                defaults={'quantity': item.quantity}
            )
            if not created:
                user_item.quantity += item.quantity
                user_item.save()
        guest_cart.delete()



# Utility to get or create a cart for the current user or session
def get_user_or_guest_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_id=session_key)
    return cart
