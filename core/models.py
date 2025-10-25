from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

# ============================================
# نماذج المستخدمين والمصادقة
# ============================================

class CustomUser(AbstractUser):
    """نموذج المستخدم المخصص مع دعم الأدوار المتعددة"""
    
    ROLE_CHOICES = [
        ('admin', _('مسؤول النظام')),
        ('manager', _('مدير')),
        ('accountant', _('محاسب')),
        ('cashier', _('كاشير')),
        ('warehouse', _('أمين مخزن')),
        ('viewer', _('عارض بيانات')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    phone = models.CharField(max_length=20, blank=True)
    is_active_status = models.BooleanField(default=True, help_text=_('هل المستخدم نشط؟'))
    last_login_branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='last_login_users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمون')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


# ============================================
# نماذج الفروع والشركات
# ============================================

class Company(models.Model):
    """نموذج الشركة الأم"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    name_ar = models.CharField(max_length=255, unique=True, verbose_name=_('الاسم بالعربية'))
    logo = models.ImageField(upload_to='companies/', null=True, blank=True)
    description = models.TextField(blank=True)
    
    # معلومات الاتصال
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    
    # العنوان
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    
    # معلومات ضريبية
    tax_id = models.CharField(max_length=50, unique=True, verbose_name=_('الرقم الضريبي'))
    commercial_register = models.CharField(max_length=50, unique=True, verbose_name=_('السجل التجاري'))
    
    # الإعدادات
    currency = models.CharField(max_length=3, default='EGP', verbose_name=_('العملة'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('شركة')
        verbose_name_plural = _('الشركات')
    
    def __str__(self):
        return self.name_ar


class Branch(models.Model):
    """نموذج الفرع/نقطة البيع"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255, verbose_name=_('الاسم بالعربية'))
    code = models.CharField(max_length=50, unique=True, verbose_name=_('كود الفرع'))
    
    # العنوان
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    
    # الإعدادات
    is_main_branch = models.BooleanField(default=False, verbose_name=_('هل هذا الفرع الرئيسي؟'))
    is_active = models.BooleanField(default=True)
    
    # الأرصدة
    opening_balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, 
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_('الرصيد الافتتاحي')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('فرع')
        verbose_name_plural = _('الفروع')
        unique_together = ('company', 'code')
        ordering = ['name_ar']
    
    def __str__(self):
        return f"{self.name_ar} ({self.code})"


# ============================================
# نماذج الفئات والمورّدين
# ============================================

class Supplier(models.Model):
    """نموذج المورّد"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='suppliers')
    name = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255, verbose_name=_('الاسم بالعربية'))
    code = models.CharField(max_length=50, unique=True, verbose_name=_('كود المورّد'))
    
    # معلومات الاتصال
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    
    # معلومات مالية
    tax_id = models.CharField(max_length=50, blank=True)
    payment_terms = models.CharField(max_length=100, blank=True, verbose_name=_('شروط الدفع'))
    
    # الأرصدة
    balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name=_('الرصيد المستحق')
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('مورّد')
        verbose_name_plural = _('الموردون')
        ordering = ['name_ar']
    
    def __str__(self):
        return self.name_ar


class Customer(models.Model):
    """نموذج العميل"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    # معلومات مالية
    balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name=_('الرصيد المستحق')
    )
    credit_limit = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name=_('حد الائتمان')
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('عميل')
        verbose_name_plural = _('العملاء')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Category(models.Model):
    """نموذج فئة المنتجات"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255, verbose_name=_('الاسم بالعربية'))
    code = models.CharField(max_length=50, unique=True, verbose_name=_('كود الفئة'))
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('فئة')
        verbose_name_plural = _('الفئات')
        ordering = ['name_ar']
    
    def __str__(self):
        return self.name_ar


# ============================================
# نماذج الوحدات والمقاييس
# ============================================

class Unit(models.Model):
    """نموذج وحدة القياس"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='units')
    name = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100, verbose_name=_('الاسم بالعربية'))
    code = models.CharField(max_length=20, unique=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('وحدة قياس')
        verbose_name_plural = _('وحدات القياس')
    
    def __str__(self):
        return self.name_ar


# ============================================
# نماذج التدقيق والسجلات
# ============================================

class AuditLog(models.Model):
    """نموذج سجل التدقيق"""
    
    ACTION_CHOICES = [
        ('create', _('إنشاء')),
        ('update', _('تحديث')),
        ('delete', _('حذف')),
        ('view', _('عرض')),
        ('login', _('تسجيل دخول')),
        ('logout', _('تسجيل خروج')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('سجل تدقيق')
        verbose_name_plural = _('سجلات التدقيق')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['model_name', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.model_name}"
