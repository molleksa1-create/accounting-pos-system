from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

# ============================================
# نماذج نقطة البيع والمبيعات
# ============================================

class SalesOrder(models.Model):
    """نموذج أمر البيع"""
    
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('submitted', _('مرسلة')),
        ('confirmed', _('مؤكدة')),
        ('shipped', _('مشحونة')),
        ('delivered', _('مسلمة')),
        ('cancelled', _('ملغاة')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='sales_orders')
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='sales_orders')
    
    order_number = models.CharField(max_length=50, unique=True, verbose_name=_('رقم الأمر'))
    customer = models.ForeignKey('core.Customer', on_delete=models.PROTECT, related_name='sales_orders')
    
    # التواريخ
    order_date = models.DateField(verbose_name=_('تاريخ الأمر'))
    expected_delivery_date = models.DateField(verbose_name=_('تاريخ التسليم المتوقع'))
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # الحالة
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # المبالغ
    subtotal = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('المجموع الفرعي')
    )
    tax_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('مبلغ الضريبة')
    )
    discount_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('مبلغ الخصم')
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الإجمالي')
    )
    
    # المسؤول
    created_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True, related_name='sales_orders_created')
    
    # ملاحظات
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('أمر بيع')
        verbose_name_plural = _('أوامر البيع')
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['customer', '-order_date']),
            models.Index(fields=['status', '-order_date']),
        ]
    
    def __str__(self):
        return self.order_number


class SalesOrderLine(models.Model):
    """نموذج سطر أمر البيع"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='lines')
    
    product = models.ForeignKey('inventory.Product', on_delete=models.PROTECT)
    
    # الكميات
    quantity = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية')
    )
    
    # الأسعار
    unit_price = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('سعر الوحدة')
    )
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('نسبة الخصم %')
    )
    line_total = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('إجمالي السطر')
    )
    
    class Meta:
        verbose_name = _('سطر أمر بيع')
        verbose_name_plural = _('أسطر أوامر البيع')
    
    def save(self, *args, **kwargs):
        discount = (self.quantity * self.unit_price) * (self.discount_percent / 100)
        self.line_total = (self.quantity * self.unit_price) - discount
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.sales_order.order_number} - {self.product.name_ar}"


class SalesInvoice(models.Model):
    """نموذج فاتورة البيع"""
    
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('submitted', _('مرسلة')),
        ('paid', _('مدفوعة')),
        ('partial', _('مدفوعة جزئياً')),
        ('cancelled', _('ملغاة')),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('نقداً')),
        ('card', _('بطاقة')),
        ('check', _('شيك')),
        ('transfer', _('تحويل بنكي')),
        ('credit', _('آجل')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='sales_invoices')
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='sales_invoices')
    
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name=_('رقم الفاتورة'))
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    customer = models.ForeignKey('core.Customer', on_delete=models.PROTECT, related_name='sales_invoices')
    
    # التواريخ
    invoice_date = models.DateField(verbose_name=_('تاريخ الفاتورة'))
    due_date = models.DateField(verbose_name=_('تاريخ الاستحقاق'))
    
    # المبالغ
    subtotal = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('المجموع الفرعي')
    )
    tax_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('مبلغ الضريبة')
    )
    discount_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('مبلغ الخصم')
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الإجمالي')
    )
    paid_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('المبلغ المدفوع')
    )
    
    # الحالة
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    
    # المسؤول
    created_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True, related_name='sales_invoices_created')
    
    # ملاحظات
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('فاتورة بيع')
        verbose_name_plural = _('فواتير البيع')
        ordering = ['-invoice_date']
        indexes = [
            models.Index(fields=['customer', '-invoice_date']),
            models.Index(fields=['status', '-invoice_date']),
        ]
    
    def __str__(self):
        return self.invoice_number


class POSSession(models.Model):
    """نموذج جلسة نقطة البيع"""
    
    STATUS_CHOICES = [
        ('open', _('مفتوحة')),
        ('closed', _('مغلقة')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='pos_sessions')
    cashier = models.ForeignKey('core.CustomUser', on_delete=models.PROTECT, related_name='pos_sessions')
    
    # الأرصدة
    opening_balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الرصيد الافتتاحي')
    )
    closing_balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الرصيد الختامي')
    )
    
    # التواريخ
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # الحالة
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    class Meta:
        verbose_name = _('جلسة نقطة بيع')
        verbose_name_plural = _('جلسات نقاط البيع')
        ordering = ['-opened_at']
    
    def __str__(self):
        return f"{self.branch.name_ar} - {self.opened_at}"


class POSTransaction(models.Model):
    """نموذج معاملة نقطة البيع"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(POSSession, on_delete=models.CASCADE, related_name='transactions')
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='pos_transactions')
    
    # الكمية والسعر
    quantity = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية')
    )
    unit_price = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('سعر الوحدة')
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الإجمالي')
    )
    
    # التاريخ
    transaction_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('معاملة نقطة بيع')
        verbose_name_plural = _('معاملات نقاط البيع')
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"معاملة - {self.session.branch.name_ar}"
