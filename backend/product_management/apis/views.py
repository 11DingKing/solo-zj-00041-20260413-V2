from typing import cast
from rest_framework import generics, status
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import action
from product_management.apis.serializers import (
    ProductSerializer,
    StockAlertSerializer,
    StockAlertCountSerializer,
    InventoryChangeLogSerializer,
    ProductUpdateStockSerializer
)
from product_management.models import Product, StockAlert, InventoryChangeLog
from product_management.services import InventoryService, AlertService
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class ProductsListView(ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)


class StockAlertViewSet(ModelViewSet):
    queryset = StockAlert.objects.all()
    serializer_class = StockAlertSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'email_sent']
    search_fields = ['product__name']
    ordering_fields = ['created_at', 'updated_at', 'current_stock']

    def get_queryset(self):
        queryset = StockAlert.objects.select_related(
            'product', 'last_change_log'
        ).all()
        return queryset

    @action(detail=False, methods=['get'])
    def pending(self, request):
        pending_alerts = AlertService.get_pending_alerts()
        serializer = self.get_serializer(pending_alerts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def count(self, request):
        count = AlertService.get_pending_alerts_count()
        return Response({'pending_count': count})

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = AlertService.resolve_alert(pk)
        if alert:
            serializer = self.get_serializer(alert)
            return Response(serializer.data)
        return Response(
            {'error': 'Alert not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True, methods=['post'])
    def send_email(self, request, pk=None):
        try:
            alert = self.get_object()
            success = AlertService.send_alert_email(alert)
            if success:
                return Response({'status': 'email sent'})
            return Response(
                {'error': 'Failed to send email'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except StockAlert.DoesNotExist:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class InventoryChangeLogViewSet(ReadOnlyModelViewSet):
    queryset = InventoryChangeLog.objects.all()
    serializer_class = InventoryChangeLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['change_type', 'product']
    search_fields = ['product__name', 'reason']
    ordering_fields = ['created_at']

    def get_queryset(self):
        queryset = InventoryChangeLog.objects.select_related(
            'product', 'created_by'
        ).all()
        return queryset

    @action(detail=False, methods=['get'])
    def by_product(self, request):
        product_id = request.query_params.get('product_id')
        if product_id:
            logs = self.get_queryset().filter(product_id=product_id)
            serializer = self.get_serializer(logs, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'product_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ProductStockUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk=None):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductUpdateStockSerializer(data=request.data)
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            change_type = serializer.validated_data['change_type']
            reason = serializer.validated_data.get('reason', '')

            try:
                change_log = InventoryService.update_stock(
                    product=product,
                    quantity=quantity,
                    change_type=change_type,
                    reason=reason,
                    user=request.user if request.user.is_authenticated else None
                )
                return Response({
                    'status': 'success',
                    'new_stock': product.total_stock,
                    'change_log_id': change_log.id
                })
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
