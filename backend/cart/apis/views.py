from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from cart.apis.serializers import CartItemSerializer, CartSerializer
from cart.models import Cart
from cart.mixins import CartTokenMixin
from cart.services import CartService


class CartListCreateView(ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartAPIView(CartTokenMixin, APIView):
    token_param = "token"
    cart = None

    def get_cart(self):
        (data, cart_data, response_status) = self.get_cart_from_token()
        if cart_data is None:
            cart = Cart()
            if self.request.user.is_authenticated:
                cart.user = self.request.user
            cart.save()
            response_data = {
                'cart_id': str(cart.id)
            }
            self.create_token(response_data)
            cart_data = cart
        return cart_data

    def get(self, request, format=None):
        cart_data = CartService.get_cart(request.user, request)
        return Response(cart_data)

    def post(self, request, format=None):
        action = request.data.get('action')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not action:
            return Response(
                {'error': 'Action is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if action == 'add':
                if not product_id:
                    return Response(
                        {'error': 'product_id is required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_data = CartService.add_to_cart(
                    request.user, request, product_id, quantity
                )
                return Response(cart_data)

            elif action == 'update':
                if not product_id:
                    return Response(
                        {'error': 'product_id is required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_data = CartService.update_cart_item(
                    request.user, request, product_id, quantity
                )
                return Response(cart_data)

            elif action == 'remove':
                if not product_id:
                    return Response(
                        {'error': 'product_id is required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_data = CartService.remove_from_cart(
                    request.user, request, product_id
                )
                return Response(cart_data)

            elif action == 'clear':
                cart_data = CartService.clear_cart(
                    request.user, request
                )
                return Response(cart_data)

            elif action == 'merge':
                if not request.user.is_authenticated:
                    return Response(
                        {'error': 'User must be authenticated to merge cart'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                cart_data = CartService.merge_session_cart_to_user_cart(
                    request.user, request
                )
                return Response(cart_data)

            else:
                return Response(
                    {'error': f'Invalid action: {action}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
