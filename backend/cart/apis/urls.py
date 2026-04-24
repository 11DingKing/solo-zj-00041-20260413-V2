from django.urls import path
from cart.apis.views import (CartAPIView, CartListCreateView)

urlpatterns = [
    path('carts/', CartListCreateView.as_view(), name='cart_list'),
    path('cart/', CartAPIView.as_view(), name='cart_api'),
]
