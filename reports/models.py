from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

# ============================================
# نماذج التقارير والتحليلات
# ============================================

class Report(models.Model):
    """نموذج التقرير"""
    
    REPORT_TYPE_CHOICES = [
        ('sales', _('تقرير المبيعات')),
        ('purchases', _('تقرير المشتريات')),
        ('inventory', _('تقرير المخزون')),
        ('financial', _('التقرير المالي')),
        ('production', _('تقرير الإنتاج')),
        ('customer', _('تقرير العملاء')),
        ('supplier', _('تقرير الموردين')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='reports')
    
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    
    # الفترة الزمنية
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(verbose_name=_('تاريخ النهاية'))
    
    # البيانات
    data = models.JSONField(default=dict, verbose_name=_('بيانات التقرير'))
    
    # المسؤول
    created_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True, related_name='reports')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('تقرير')
        verbose_name_plural = _('التقارير')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type', '-created_at']),
        ]
    
    def __str__(self):
        return self.name


class SalesReport(models.Model):
    """نموذج تقرير المبيعات"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='sales_reports')
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_reports')
    
    # الفترة الزمنية
    report_date = models.DateField(verbose_name=_('تاريخ التقرير'))
    
    # الإحصائيات
    total_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_items_sold = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # عدد الفواتير
    invoice_count = models.IntegerField(default=0)
    
    # البيانات التفصيلية
    data = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('تقرير مبيعات')
        verbose_name_plural = _('تقارير المبيعات')
        ordering = ['-report_date']
        unique_together = ('company', 'branch', 'report_date')
    
    def __str__(self):
        return f"تقرير مبيعات - {self.report_date}"


class InventoryReport(models.Model):
    """نموذج تقرير المخزون"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='inventory_reports')
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_reports')
    
    # الفترة الزمنية
    report_date = models.DateField(verbose_name=_('تاريخ التقرير'))
    
    # الإحصائيات
    total_items = models.IntegerField(default=0, verbose_name=_('إجمالي المنتجات'))
    total_quantity = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('إجمالي الكمية'))
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('إجمالي القيمة'))
    
    # المنتجات ذات المخزون المنخفض
    low_stock_items = models.IntegerField(default=0, verbose_name=_('منتجات بمخزون منخفض'))
    
    # البيانات التفصيلية
    data = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('تقرير مخزون')
        verbose_name_plural = _('تقارير المخزون')
        ordering = ['-report_date']
        unique_together = ('company', 'branch', 'report_date')
    
    def __str__(self):
        return f"تقرير مخزون - {self.report_date}"


class FinancialReport(models.Model):
    """نموذج التقرير المالي"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='financial_reports')
    
    # الفترة الزمنية
    start_date = models.DateField(verbose_name=_('تاريخ البداية'))
    end_date = models.DateField(verbose_name=_('تاريخ النهاية'))
    
    # الإيرادات
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('إجمالي الإيرادات'))
    
    # المصروفات
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('إجمالي المصروفات'))
    
    # الأرباح
    gross_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('إجمالي الأرباح'))
    net_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_('صافي الأرباح'))
    
    # البيانات التفصيلية
    data = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('تقرير مالي')
        verbose_name_plural = _('التقارير المالية')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"تقرير مالي - {self.start_date} إلى {self.end_date}"


class DashboardMetric(models.Model):
    """نموذج مقياس لوحة التحكم"""
    
    METRIC_TYPE_CHOICES = [
        ('sales', _('المبيعات')),
        ('purchases', _('المشتريات')),
        ('inventory', _('المخزون')),
        ('profit', _('الأرباح')),
        ('customers', _('العملاء')),
        ('suppliers', _('الموردين')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='dashboard_metrics')
    
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPE_CHOICES)
    metric_date = models.DateField(verbose_name=_('تاريخ المقياس'))
    
    # القيمة
    value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # المقارنة مع الفترة السابقة
    previous_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    change_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_('نسبة التغيير %'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('مقياس لوحة تحكم')
        verbose_name_plural = _('مقاييس لوحة التحكم')
        ordering = ['-metric_date']
        unique_together = ('company', 'metric_type', 'metric_date')
    
    def __str__(self):
        return f"{self.get_metric_type_display()} - {self.metric_date}"
