from django.db import models
from django.utils.translation import gettext_lazy as _
from uuid import uuid4
from core.models import Company, Branch, Customer
from pos.models import SalesInvoice

class DeliveryPlatform(models.Model):
    """منصات التوصيل المدعومة"""
    PLATFORM_CHOICES = [
        ('hanger', 'Hanger Station'),
        ('kita', 'Kita'),
        ('uber_eats', 'Uber Eats'),
        ('zomato', 'Zomato'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='delivery_platforms')
    platform_name = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    api_key = models.CharField(max_length=500, blank=True)
    api_secret = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('منصة توصيل')
        verbose_name_plural = _('منصات التوصيل')
        unique_together = ('company', 'platform_name')
    
    def __str__(self):
        return f"{self.company.name_ar} - {self.get_platform_name_display()}"

class DeliveryOrder(models.Model):
    """طلبات التوصيل"""
    STATUS_CHOICES = [
        ('pending', _('في الانتظار')),
        ('confirmed', _('مؤكد')),
        ('preparing', _('قيد التحضير')),
        ('ready', _('جاهز')),
        ('on_the_way', _('في الطريق')),
        ('delivered', _('تم التسليم')),
        ('cancelled', _('ملغى')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    sales_invoice = models.OneToOneField(SalesInvoice, on_delete=models.CASCADE, related_name='delivery_order')
    platform = models.ForeignKey(DeliveryPlatform, on_delete=models.SET_NULL, null=True)
    platform_order_id = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    delivery_address = models.TextField()
    delivery_phone = models.CharField(max_length=20)
    delivery_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    driver_name = models.CharField(max_length=100, blank=True)
    driver_phone = models.CharField(max_length=20, blank=True)
    driver_location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('طلب توصيل')
        verbose_name_plural = _('طلبات التوصيل')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"طلب توصيل #{self.platform_order_id}"

class DeliveryTracking(models.Model):
    """تتبع حالة التوصيل"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    delivery_order = models.ForeignKey(DeliveryOrder, on_delete=models.CASCADE, related_name='tracking_history')
    status = models.CharField(max_length=20, choices=DeliveryOrder.STATUS_CHOICES)
    location = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('تتبع التوصيل')
        verbose_name_plural = _('تتبع التوصيل')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"تتبع #{self.delivery_order.platform_order_id}"

class DeliveryIntegrationLog(models.Model):
    """سجل التكامل مع منصات التوصيل"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    platform = models.ForeignKey(DeliveryPlatform, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # create_order, update_status, cancel_order
    request_data = models.JSONField()
    response_data = models.JSONField()
    status_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    is_success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('سجل التكامل')
        verbose_name_plural = _('سجلات التكامل')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.platform.get_platform_name_display()} - {self.action}"
