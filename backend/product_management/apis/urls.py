from django.urls import path
from rest_framework.routers import DefaultRouter
from product_management.apis.views import (
    ProductsListView,
    StockAlertViewSet,
    InventoryChangeLogViewSet,
    ProductStockUpdateView
)

router = DefaultRouter()
router.register(r'stock-alerts', StockAlertViewSet, basename='stock-alerts')
router.register(r'inventory-logs', InventoryChangeLogViewSet, basename='inventory-logs')

urlpatterns = [
    path('products/',
         ProductsListView.as_view({'get': 'list'}), name='products-list'),
    path('products/<str:slug>',
         ProductsListView.as_view({'get': 'retrieve'}), name='products_detail'),
    path('products/<int:pk>/update-stock/',
         ProductStockUpdateView.as_view(), name='product-update-stock'),
]

urlpatterns += router.urls
