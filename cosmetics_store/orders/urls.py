from django.urls import path
from .views import CreateInstantCheckoutView, CreateOrderFromCartView, InstantCheckoutDetailView, PlaceOrderView

urlpatterns = [
    path("instant/", CreateInstantCheckoutView.as_view(), name="instant-checkout"),
    path("instant/<uuid:pk>/", InstantCheckoutDetailView.as_view(), name="instant-checkout-detail"),
    path("instant/place-order/", PlaceOrderView.as_view(), name="instant-place-order"),
    path("place-order/", CreateOrderFromCartView.as_view(), name="place-order"),
]