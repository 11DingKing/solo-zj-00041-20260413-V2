from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from product_management.models import Product, InventoryChangeLog, StockAlert


class InventoryService:
    @staticmethod
    @transaction.atomic
    def update_stock(product, quantity, change_type, reason=None, user=None):
        previous_stock = product.total_stock
        
        if change_type == InventoryChangeLog.DECREASE:
            if product.total_stock < quantity:
                raise ValueError(f"Insufficient stock. Available: {product.total_stock}, Requested: {quantity}")
            product.total_stock -= quantity
        elif change_type == InventoryChangeLog.INCREASE:
            product.total_stock += quantity
        
        product.save()
        
        change_log = InventoryChangeLog.objects.create(
            product=product,
            change_type=change_type,
            quantity=quantity,
            previous_stock=previous_stock,
            new_stock=product.total_stock,
            reason=reason,
            created_by=user
        )
        
        AlertService.check_and_create_alert(product, change_log)
        
        return change_log


class AlertService:
    @staticmethod
    def check_and_create_alert(product, change_log=None):
        pending_alert = StockAlert.objects.filter(
            product=product,
            status=StockAlert.PENDING
        ).first()
        
        if product.total_stock <= product.min_stock_threshold:
            if pending_alert:
                pending_alert.current_stock = product.total_stock
                pending_alert.threshold = product.min_stock_threshold
                if change_log:
                    pending_alert.last_change_log = change_log
                pending_alert.save()
                
                if not pending_alert.email_sent:
                    AlertService.send_alert_email(pending_alert)
            else:
                alert = StockAlert.objects.create(
                    product=product,
                    current_stock=product.total_stock,
                    threshold=product.min_stock_threshold,
                    status=StockAlert.PENDING,
                    last_change_log=change_log
                )
                AlertService.send_alert_email(alert)
        else:
            if pending_alert:
                pending_alert.status = StockAlert.RESOLVED
                pending_alert.save()
    
    @staticmethod
    def send_alert_email(alert):
        admin_emails = getattr(settings, 'STOCK_ALERT_RECIPIENTS', [])
        
        if not admin_emails:
            if settings.ADMINS:
                admin_emails = [admin[1] for admin in settings.ADMINS]
        
        if not admin_emails:
            return False
        
        subject = f"Stock Alert: {alert.product.name} is running low"
        message = f"""
        Stock Alert Notification
        
        Product: {alert.product.name}
        Current Stock: {alert.current_stock}
        Minimum Threshold: {alert.threshold}
        
        Please restock this product as soon as possible.
        
        This is an automated notification.
        """
        
        from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com'
        
        try:
            send_mail(
                subject,
                message,
                from_email,
                admin_emails,
                fail_silently=False,
            )
            alert.email_sent = True
            alert.save()
            return True
        except Exception as e:
            print(f"Failed to send stock alert email: {e}")
            return False
    
    @staticmethod
    def get_pending_alerts_count():
        return StockAlert.objects.filter(status=StockAlert.PENDING).count()
    
    @staticmethod
    def get_pending_alerts():
        return StockAlert.objects.filter(
            status=StockAlert.PENDING
        ).select_related('product', 'last_change_log').order_by('-created_at')
    
    @staticmethod
    def resolve_alert(alert_id):
        try:
            alert = StockAlert.objects.get(id=alert_id)
            alert.status = StockAlert.RESOLVED
            alert.save()
            return alert
        except StockAlert.DoesNotExist:
            return None
