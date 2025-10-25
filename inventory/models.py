from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

# ============================================
# نماذج المنتجات والمخزون
# ============================================

class Product(models.Model):
    """نموذج المنتج"""
    
    PRODUCT_TYPE_CHOICES = [
        ('raw_material', _('مادة خام')),
        ('finished_good', _('منتج نهائي')),
        ('service', _('خدمة')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255, verbose_name=_('الاسم بالعربية'))
    code = models.CharField(max_length=50, unique=True, verbose_name=_('كود المنتج'))
    barcode = models.CharField(max_length=100, unique=True, blank=True, verbose_name=_('الباركود'))
    
    # التصنيف
    category = models.ForeignKey('core.Category', on_delete=models.SET_NULL, null=True, related_name='products')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default='finished_good')
    
    # الوصف والصورة
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    
    # الوحدة الأساسية
    unit = models.ForeignKey('core.Unit', on_delete=models.PROTECT, related_name='products')
    
    # الأسعار
    cost_price = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('سعر التكلفة')
    )
    selling_price = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('سعر البيع')
    )
    
    # المخزون
    quantity_on_hand = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المتاحة')
    )
    reorder_level = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('حد إعادة الطلب')
    )
    reorder_quantity = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('كمية إعادة الطلب')
    )
    
    # الحالة
    is_active = models.BooleanField(default=True)
    track_quantity = models.BooleanField(default=True, verbose_name=_('تتبع الكمية'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('منتج')
        verbose_name_plural = _('المنتجات')
        ordering = ['name_ar']
        indexes = [
            models.Index(fields=['company', 'code']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.name_ar


class InventoryMovement(models.Model):
    """نموذج حركة المخزون"""
    
    MOVEMENT_TYPE_CHOICES = [
        ('purchase', _('شراء')),
        ('sale', _('بيع')),
        ('adjustment', _('تعديل')),
        ('transfer', _('تحويل بين فروع')),
        ('production', _('إنتاج')),
        ('return', _('إرجاع')),
        ('damage', _('تلف')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='inventory_movements')
    
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية')
    )
    unit_price = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name=_('سعر الوحدة')
    )
    
    # المراجع
    reference_type = models.CharField(max_length=50, blank=True)  # purchase_order, sale_order, etc.
    reference_id = models.CharField(max_length=100, blank=True)
    
    # التفاصيل
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('حركة مخزون')
        verbose_name_plural = _('حركات المخزون')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'branch', '-created_at']),
            models.Index(fields=['movement_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.product.name_ar} - {self.get_movement_type_display()}"


class StockLevel(models.Model):
    """نموذج مستوى المخزون في كل فرع"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_levels')
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='stock_levels')
    
    quantity = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية')
    )
    
    last_counted_at = models.DateTimeField(null=True, blank=True, verbose_name=_('آخر جرد'))
    last_counted_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('مستوى مخزون')
        verbose_name_plural = _('مستويات المخزون')
        unique_together = ('product', 'branch')
        indexes = [
            models.Index(fields=['branch', 'quantity']),
        ]
    
    def __str__(self):
        return f"{self.product.name_ar} - {self.branch.name_ar}"


class InventoryAdjustment(models.Model):
    """نموذج تعديل المخزون (جرد فعلي)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='adjustments')
    
    adjustment_date = models.DateField(verbose_name=_('تاريخ التعديل'))
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True, related_name='adjustments_created')
    approved_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='adjustments_approved')
    
    is_approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('تعديل مخزون')
        verbose_name_plural = _('تعديلات المخزون')
        ordering = ['-adjustment_date']
    
    def __str__(self):
        return f"تعديل مخزون - {self.branch.name_ar} - {self.adjustment_date}"


class AdjustmentLine(models.Model):
    """نموذج سطر تعديل المخزون"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    adjustment = models.ForeignKey(InventoryAdjustment, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    system_quantity = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية بالنظام')
    )
    actual_quantity = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية الفعلية')
    )
    
    difference = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name=_('الفرق')
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('سطر تعديل')
        verbose_name_plural = _('أسطر التعديل')
    
    def save(self, *args, **kwargs):
        self.difference = self.actual_quantity - self.system_quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name_ar} - {self.difference}"


class WarehouseLocation(models.Model):
    """نموذج موقع المخزن"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='warehouse_locations')
    
    location_code = models.CharField(max_length=50, unique=True, verbose_name=_('كود الموقع'))
    description = models.CharField(max_length=255, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('موقع مخزن')
        verbose_name_plural = _('مواقع المخازن')
    
    def __str__(self):
        return self.location_code
