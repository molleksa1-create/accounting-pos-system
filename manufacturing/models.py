from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

# ============================================
# نماذج الوصفات والإنتاج
# ============================================

class Recipe(models.Model):
    """نموذج الوصفة (التركيبة)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='recipes')
    
    name = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255, verbose_name=_('الاسم بالعربية'))
    code = models.CharField(max_length=50, unique=True, verbose_name=_('كود الوصفة'))
    
    # المنتج النهائي
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='recipes')
    
    # الكمية المنتجة
    output_quantity = models.DecimalField(
        max_digits=15, decimal_places=2, default=1,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المنتجة')
    )
    
    # الوصف
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True, verbose_name=_('التعليمات'))
    
    # الوقت
    production_time_minutes = models.IntegerField(default=0, verbose_name=_('وقت الإنتاج (دقيقة)'))
    
    # الحالة
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('وصفة')
        verbose_name_plural = _('الوصفات')
        ordering = ['name_ar']
    
    def __str__(self):
        return self.name_ar


class RecipeIngredient(models.Model):
    """نموذج مكونات الوصفة"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    
    # مكون الوصفة (مادة خام)
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='recipe_ingredients')
    
    # الكمية المطلوبة
    quantity = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية')
    )
    
    # الوحدة
    unit = models.ForeignKey('core.Unit', on_delete=models.PROTECT)
    
    # النسبة من المنتج النهائي
    is_main_ingredient = models.BooleanField(default=False, verbose_name=_('مكون رئيسي'))
    
    class Meta:
        verbose_name = _('مكون وصفة')
        verbose_name_plural = _('مكونات الوصفات')
        unique_together = ('recipe', 'product')
    
    def __str__(self):
        return f"{self.recipe.name_ar} - {self.product.name_ar}"


class ProductionOrder(models.Model):
    """نموذج أمر الإنتاج"""
    
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('planned', _('مخططة')),
        ('in_progress', _('قيد التنفيذ')),
        ('completed', _('مكتملة')),
        ('cancelled', _('ملغاة')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='production_orders')
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, related_name='production_orders')
    
    order_number = models.CharField(max_length=50, unique=True, verbose_name=_('رقم الأمر'))
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT)
    
    # الكميات
    planned_quantity = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المخططة')
    )
    produced_quantity = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المنتجة')
    )
    
    # التواريخ
    planned_start_date = models.DateTimeField(verbose_name=_('تاريخ بداية مخطط'))
    planned_end_date = models.DateTimeField(verbose_name=_('تاريخ نهاية مخطط'))
    actual_start_date = models.DateTimeField(null=True, blank=True)
    actual_end_date = models.DateTimeField(null=True, blank=True)
    
    # الحالة
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # المسؤولون
    created_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True, related_name='production_orders_created')
    assigned_to = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='production_orders_assigned')
    
    # ملاحظات
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('أمر إنتاج')
        verbose_name_plural = _('أوامر الإنتاج')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['branch', '-created_at']),
        ]
    
    def __str__(self):
        return self.order_number


class ProductionOrderLine(models.Model):
    """نموذج سطر أمر الإنتاج (مع مكونات مختلفة)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='lines')
    
    ingredient = models.ForeignKey(RecipeIngredient, on_delete=models.PROTECT)
    
    # الكميات
    planned_quantity = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المخططة')
    )
    consumed_quantity = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الكمية المستهلكة')
    )
    
    class Meta:
        verbose_name = _('سطر أمر إنتاج')
        verbose_name_plural = _('أسطر أوامر الإنتاج')
    
    def __str__(self):
        return f"{self.production_order.order_number} - {self.ingredient.product.name_ar}"
