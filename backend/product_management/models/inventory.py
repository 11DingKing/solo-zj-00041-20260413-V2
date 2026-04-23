from django.db import models
from django.contrib.auth import get_user_model
from product_management.models import Product

User = get_user_model()


class InventoryChangeLog(models.Model):
    INCREASE = 'increase'
    DECREASE = 'decrease'
    CHANGE_TYPE_CHOICES = [
        (INCREASE, 'Increase'),
        (DECREASE, 'Decrease'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory_changes'
    )
    change_type = models.CharField(
        max_length=20,
        choices=CHANGE_TYPE_CHOICES
    )
    quantity = models.IntegerField()
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Inventory Change Log'
        verbose_name_plural = 'Inventory Change Logs'

    def __str__(self):
        return f"{self.product.name} - {self.change_type} - {self.quantity}"


class StockAlert(models.Model):
    PENDING = 'pending'
    RESOLVED = 'resolved'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (RESOLVED, 'Resolved'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_alerts'
    )
    current_stock = models.IntegerField()
    threshold = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    email_sent = models.BooleanField(default=False)
    last_change_log = models.ForeignKey(
        InventoryChangeLog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Stock Alert'
        verbose_name_plural = 'Stock Alerts'

    def __str__(self):
        return f"Alert: {self.product.name} - Stock: {self.current_stock}, Threshold: {self.threshold}"
