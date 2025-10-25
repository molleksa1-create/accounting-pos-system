from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

# ============================================
# نماذج الفواتير والمشتريات
# ============================================

class PurchaseOrder(models.Model):
    """نموذج أمر الشراء"""
    
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('submitted', _('مرسلة')),
        ('confirmed', _('مؤكدة')),
        ('partial', _('استقبال جزئي')),
        ('received', _('مستقبلة')),
        ('cancelled', _('ملغاة')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='purchase_orders')
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='purchase_orders')
    
    order_number = models.CharField(max_length=50, unique=True, verbose_name=_('رقم الأمر'))
    supplier = models.ForeignKey('core.Supplier', on_delete=models.PROTECT, related_name='purchase_orders')
    
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
    created_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True, related_name='purchase_orders_created')
    
    # ملاحظات
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('أمر شراء')
        verbose_name_plural = _('أوامر الشراء')
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['supplier', '-order_date']),
            models.Index(fields=['status', '-order_date']),
        ]
    
    def __str__(self):
        return self.order_number


class PurchaseOrderLine(models.Model):
    """نموذج سطر أمر الشراء"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='lines')
    
    product = models.ForeignKey('inventory.Product', on_delete=models.PROTECT)
    
    # الكميات
    quantity = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية')
    )
    received_quantity = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المستقبلة')
    )
    
    # الأسعار
    unit_price = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('سعر الوحدة')
    )
    line_total = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('إجمالي السطر')
    )
    
    class Meta:
        verbose_name = _('سطر أمر شراء')
        verbose_name_plural = _('أسطر أوامر الشراء')
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.purchase_order.order_number} - {self.product.name_ar}"


class GoodsReceipt(models.Model):
    """نموذج إيصال استقبال البضائع"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='goods_receipts')
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='goods_receipts')
    
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name=_('رقم الإيصال'))
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='receipts')
    
    receipt_date = models.DateField(verbose_name=_('تاريخ الاستقبال'))
    
    # المسؤول
    received_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True, related_name='goods_receipts')
    
    # ملاحظات
    notes = models.TextField(blank=True)
    
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='goods_receipts_approved')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('إيصال استقبال')
        verbose_name_plural = _('إيصالات الاستقبال')
        ordering = ['-receipt_date']
    
    def __str__(self):
        return self.receipt_number


class GoodsReceiptLine(models.Model):
    """نموذج سطر إيصال الاستقبال"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goods_receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name='lines')
    
    purchase_order_line = models.ForeignKey(PurchaseOrderLine, on_delete=models.PROTECT)
    
    # الكميات
    quantity_received = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المستقبلة')
    )
    quantity_accepted = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المقبولة')
    )
    quantity_rejected = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المرفوضة')
    )
    
    # ملاحظات
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('سطر إيصال استقبال')
        verbose_name_plural = _('أسطر إيصالات الاستقبال')
    
    def __str__(self):
        return f"{self.goods_receipt.receipt_number} - {self.purchase_order_line.product.name_ar}"


class PurchaseInvoice(models.Model):
    """نموذج فاتورة الشراء"""
    
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('submitted', _('مرسلة')),
        ('approved', _('موافق عليها')),
        ('paid', _('مدفوعة')),
        ('cancelled', _('ملغاة')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='purchase_invoices')
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='purchase_invoices')
    
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name=_('رقم الفاتورة'))
    supplier_invoice_number = models.CharField(max_length=50, blank=True, verbose_name=_('رقم فاتورة المورد'))
    supplier = models.ForeignKey('core.Supplier', on_delete=models.PROTECT, related_name='purchase_invoices')
    
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
    
    # المسؤول
    created_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True, related_name='purchase_invoices_created')
    
    # ملاحظات
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('فاتورة شراء')
        verbose_name_plural = _('فواتير الشراء')
        ordering = ['-invoice_date']
        indexes = [
            models.Index(fields=['supplier', '-invoice_date']),
            models.Index(fields=['status', '-invoice_date']),
        ]
    
    def __str__(self):
        return self.invoice_number
