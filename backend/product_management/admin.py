from django.contrib import admin
from .models import (Product,
                     ProductType,
                     ProductAttributes,
                     ProductSpecification,
                     ProductSpecificationValue,
                     ProductImage,
                     InventoryChangeLog,
                     StockAlert
                     )


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [
        ProductSpecificationInline
    ]


class ProductImageInline(admin.TabularInline):
    model = ProductImage


class ProductSpecificationValueInline(admin.TabularInline):
    model = ProductSpecificationValue


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductSpecificationValueInline,
        ProductImageInline,
    ]
    list_display = ['name', 'category', 'total_stock', 'min_stock_threshold', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'product_type')
        }),
        ('Pricing', {
            'fields': ('regular_price', 'discount_price')
        }),
        ('Inventory', {
            'fields': ('total_stock', 'min_stock_threshold')
        }),
        ('Description', {
            'fields': ('short_description', 'description')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InventoryChangeLog)
class InventoryChangeLogAdmin(admin.ModelAdmin):
    list_display = ['product', 'change_type', 'quantity', 'previous_stock', 'new_stock', 'created_at', 'created_by']
    list_filter = ['change_type', 'created_at']
    search_fields = ['product__name', 'reason']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'current_stock', 'threshold', 'status', 'email_sent', 'created_at', 'updated_at']
    list_filter = ['status', 'email_sent', 'created_at']
    search_fields = ['product__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    actions = ['mark_as_resolved', 'send_email_alert']
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status=StockAlert.RESOLVED)
    mark_as_resolved.short_description = "Mark selected alerts as resolved"
    
    def send_email_alert(self, request, queryset):
        from product_management.services import AlertService
        for alert in queryset:
            AlertService.send_alert_email(alert)
    send_email_alert.short_description = "Send email alert for selected"
