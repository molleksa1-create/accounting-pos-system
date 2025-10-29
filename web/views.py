from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from core.models import Company, Branch, Customer, Supplier
from inventory.models import Product
from accounting.models import PurchaseInvoice
from pos.models import SalesInvoice
from manufacturing.models import ProductionOrder

def index(request):
    """الصفحة الرئيسية - بدون تسجيل دخول"""
    # إذا كان المستخدم مسجل دخول، اذهب إلى لوحة التحكم
    if request.user.is_authenticated:
        return dashboard(request)
    
    # الحصول على الشركة والفرع الأول
    company = Company.objects.first()
    branch = Branch.objects.first() if company else None
    
    if not company or not branch:
        return render(request, 'web/welcome.html')
    
    # إحصائيات عامة
    today = timezone.now().date()
    
    today_sales = SalesInvoice.objects.filter(
        branch=branch,
        invoice_date=today
    ).aggregate(
        total=Sum('total_amount'),
        count=Count('id')
    )
    
    today_purchases = PurchaseInvoice.objects.filter(
        branch=branch,
        invoice_date=today
    ).aggregate(
        total=Sum('total_amount'),
        count=Count('id')
    )
    
    total_products = Product.objects.filter(company=company).count()
    total_customers = Customer.objects.filter(company=company).count()
    total_suppliers = Supplier.objects.filter(company=company).count()
    
    context = {
        'company': company,
        'branch': branch,
        'today_sales_total': today_sales['total'] or 0,
        'today_sales_count': today_sales['count'] or 0,
        'today_purchases_total': today_purchases['total'] or 0,
        'today_purchases_count': today_purchases['count'] or 0,
        'total_products': total_products,
        'total_customers': total_customers,
        'total_suppliers': total_suppliers,
    }
    
    return render(request, 'web/index.html', context)

@login_required(login_url='admin:login')
def dashboard(request):
    """لوحة التحكم الرئيسية"""
    user = request.user
    
    # الحصول على الشركة والفرع
    company = user.branch.company if user.branch else None
    branch = user.branch
    
    if not company:
        return render(request, 'web/no_access.html')
    
    # إحصائيات اليوم
    today = timezone.now().date()
    
    # المبيعات
    today_sales = SalesInvoice.objects.filter(
        company=company,
        branch=branch,
        invoice_date=today
    ).aggregate(
        total=Sum('total_amount'),
        count=Count('id')
    )
    
    # الشراء
    today_purchases = PurchaseInvoice.objects.filter(
        company=company,
        branch=branch,
        invoice_date=today
    ).aggregate(
        total=Sum('total_amount'),
        count=Count('id')
    )
    
    # المخزون
    products = Product.objects.filter(company=company)
    total_products = products.count()
    low_stock = products.filter(quantity_on_hand__lt=50).count()
    
    # أحدث الفواتير
    recent_sales = SalesInvoice.objects.filter(
        company=company,
        branch=branch
    ).order_by('-invoice_date')[:5]
    
    recent_purchases = PurchaseInvoice.objects.filter(
        company=company,
        branch=branch
    ).order_by('-invoice_date')[:5]
    
    # الإحصائيات الشهرية
    month_start = today.replace(day=1)
    month_sales = SalesInvoice.objects.filter(
        company=company,
        branch=branch,
        invoice_date__gte=month_start
    ).aggregate(total=Sum('total_amount'))
    
    month_purchases = PurchaseInvoice.objects.filter(
        company=company,
        branch=branch,
        invoice_date__gte=month_start
    ).aggregate(total=Sum('total_amount'))
    
    context = {
        'company': company,
        'branch': branch,
        'today_sales': today_sales,
        'today_purchases': today_purchases,
        'total_products': total_products,
        'low_stock': low_stock,
        'recent_sales': recent_sales,
        'recent_purchases': recent_purchases,
        'month_sales': month_sales['total'] or Decimal('0'),
        'month_purchases': month_purchases['total'] or Decimal('0'),
    }
    
    return render(request, 'web/dashboard.html', context)


@login_required
def products_list(request):
    """قائمة المنتجات"""
    user = request.user
    company = user.branch.company if user.branch else None
    
    if not company:
        return render(request, 'web/no_access.html')
    
    products = Product.objects.filter(company=company).order_by('name_ar')
    
    context = {
        'products': products,
        'company': company,
    }
    
    return render(request, 'web/products_list.html', context)


@login_required
def sales_report(request):
    """تقرير المبيعات"""
    user = request.user
    company = user.branch.company if user.branch else None
    
    if not company:
        return render(request, 'web/no_access.html')
    
    # الحصول على تاريخ البداية والنهاية
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    sales = SalesInvoice.objects.filter(company=company)
    
    if from_date:
        sales = sales.filter(invoice_date__gte=from_date)
    if to_date:
        sales = sales.filter(invoice_date__lte=to_date)
    
    sales = sales.order_by('-invoice_date')
    
    # الإجمالي
    total = sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    context = {
        'sales': sales,
        'company': company,
        'total': total,
        'from_date': from_date,
        'to_date': to_date,
    }
    
    return render(request, 'web/sales_report.html', context)


@login_required
def inventory_report(request):
    """تقرير المخزون"""
    user = request.user
    company = user.branch.company if user.branch else None
    
    if not company:
        return render(request, 'web/no_access.html')
    
    products = Product.objects.filter(company=company).order_by('name_ar')
    
    # إحصائيات
    total_value = sum(p.quantity_on_hand * p.selling_price for p in products)
    low_stock = products.filter(quantity_on_hand__lt=50)
    
    context = {
        'products': products,
        'company': company,
        'total_value': total_value,
        'low_stock': low_stock,
    }
    
    return render(request, 'web/inventory_report.html', context)
