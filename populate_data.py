import os
import django
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Company, Branch, Category, Unit, Supplier, Customer
from inventory.models import Product
from accounting.models import PurchaseOrder, PurchaseOrderLine, PurchaseInvoice
from pos.models import SalesOrder, SalesOrderLine, SalesInvoice

print("🔄 جاري إضافة البيانات التجريبية...")

# 1. إضافة شركة
company, created = Company.objects.get_or_create(
    name="Molle Bakery",
    defaults={
        "name_ar": "مخبزة مولي",
        "tax_id": "123456789",
        "commercial_register": "987654321",
        "phone": "+966501234567",
        "email": "info@mollbakery.com",
        "address": "الرياض، السعودية",
        "city": "الرياض",
        "country": "السعودية"
    }
)
print(f"✓ شركة: {company.name}")

# 2. إضافة فرع
branch, created = Branch.objects.get_or_create(
    company=company,
    code="BR-001",
    defaults={
        "name": "Main Branch",
        "name_ar": "الفرع الرئيسي",
        "phone": "+966501234567",
        "address": "شارع الملك فهد، الرياض",
        "city": "الرياض",
        "is_main_branch": True,
        "is_active": True
    }
)
print(f"✓ فرع: {branch.name_ar}")

# 3. إضافة فئات
categories = [
    ("Cakes", "كعك", "CAKES"),
    ("Pastries", "معجنات", "PASTRIES"),
    ("Cookies", "بسكويت", "COOKIES"),
    ("Bread", "خبز", "BREAD"),
]

category_objs = {}
for name_en, name_ar, code in categories:
    cat, created = Category.objects.get_or_create(
        company=company,
        code=code,
        defaults={"name": name_en, "name_ar": name_ar}
    )
    category_objs[name_en] = cat
    if created:
        print(f"✓ فئة: {name_ar}")

# 4. إضافة وحدات
units = [
    ("Piece", "قطعة", "PIECE"),
    ("Box", "صندوق", "BOX"),
    ("KG", "كيلو", "KG"),
    ("Liter", "لتر", "LITER"),
]

unit_objs = {}
for name_en, name_ar, code in units:
    unit, created = Unit.objects.get_or_create(
        company=company,
        code=code,
        defaults={"name": name_en, "name_ar": name_ar}
    )
    unit_objs[name_en] = unit
    if created:
        print(f"✓ وحدة: {name_ar}")

# 5. إضافة موردين
suppliers = [
    ("Ahmed Flour", "أحمد للدقيق", "SUP-001", "+966501111111"),
    ("Sugar Company", "شركة السكر", "SUP-002", "+966502222222"),
    ("Butter Supplier", "مورد الزبدة", "SUP-003", "+966503333333"),
]

supplier_objs = {}
for name_en, name_ar, code, phone in suppliers:
    supplier, created = Supplier.objects.get_or_create(
        company=company,
        code=code,
        defaults={
            "name": name_en,
            "name_ar": name_ar,
            "phone": phone,
            "email": f"{name_en.lower().replace(' ', '')}@supplier.com",
            "address": "جدة، السعودية"
        }
    )
    supplier_objs[name_en] = supplier
    if created:
        print(f"✓ مورد: {name_ar}")

# 6. إضافة عملاء
customers = [
    ("Mohammed Ali", "محمد علي", "+966501234567"),
    ("Fatima Hassan", "فاطمة حسن", "+966502345678"),
    ("Omar Ahmed", "عمر أحمد", "+966503456789"),
]

customer_objs = {}
for name_en, name_ar, phone in customers:
    customer, created = Customer.objects.get_or_create(
        company=company,
        name=name_en,
        defaults={
            "phone": phone,
            "email": f"{name_en.lower().replace(' ', '')}@customer.com",
            "address": "الرياض، السعودية"
        }
    )
    customer_objs[name_en] = customer
    if created:
        print(f"✓ عميل: {name_ar}")

# 7. إضافة منتجات
products = [
    ("Chocolate Cake", "كعكة الشوكولاتة", "Cakes", "PROD-001", "8901234567001", 50, 100),
    ("Vanilla Cake", "كعكة الفانيليا", "Cakes", "PROD-002", "8901234567002", 45, 80),
    ("Croissant", "كرواسان", "Pastries", "PROD-003", "8901234567003", 15, 200),
    ("Donut", "دونات", "Pastries", "PROD-004", "8901234567004", 10, 300),
    ("Chocolate Cookie", "بسكويت الشوكولاتة", "Cookies", "PROD-005", "8901234567005", 5, 500),
    ("Wheat Bread", "خبز القمح", "Bread", "PROD-006", "8901234567006", 3, 1000),
]

product_objs = {}
for name_en, name_ar, category_name, code, barcode, price, quantity in products:
    product, created = Product.objects.get_or_create(
        company=company,
        code=code,
        defaults={
            "name": name_en,
            "name_ar": name_ar,
            "barcode": barcode,
            "category": category_objs[category_name],
            "unit": unit_objs["Piece"],
            "cost_price": Decimal(str(price * 0.5)),
            "selling_price": Decimal(str(price)),
            "quantity_on_hand": quantity,
            "reorder_level": 50,
            "is_active": True
        }
    )
    product_objs[name_en] = product
    if created:
        print(f"✓ منتج: {name_ar} (السعر: {price} ريال)")

# 8. إضافة أمر شراء
purchase_order, created = PurchaseOrder.objects.get_or_create(
    company=company,
    branch=branch,
    order_number="PUR-ORD-001",
    defaults={
        "supplier": supplier_objs["Ahmed Flour"],
        "order_date": datetime.now().date(),
        "expected_delivery_date": (datetime.now() + timedelta(days=5)).date(),
        "status": "draft"
    }
)
if created:
    print(f"✓ أمر شراء: {purchase_order.order_number}")

# 9. إضافة عناصر أمر الشراء
for product_name, qty in [("Chocolate Cake", 50), ("Vanilla Cake", 30)]:
    PurchaseOrderLine.objects.get_or_create(
        purchase_order=purchase_order,
        product=product_objs[product_name],
        defaults={
            "quantity": Decimal(str(qty)),
            "unit_price": product_objs[product_name].cost_price,
            "line_total": Decimal(str(qty)) * product_objs[product_name].cost_price
        }
    )
print(f"✓ عناصر أمر الشراء")

# 10. إضافة فاتورة شراء
purchase_invoice, created = PurchaseInvoice.objects.get_or_create(
    company=company,
    branch=branch,
    invoice_number="PUR-INV-001",
    defaults={
        "supplier": supplier_objs["Ahmed Flour"],
        "invoice_date": datetime.now().date(),
        "due_date": (datetime.now() + timedelta(days=30)).date(),
        "subtotal": Decimal("2500.00"),
        "tax_amount": Decimal("250.00"),
        "discount_amount": Decimal("0.00"),
        "total_amount": Decimal("2750.00"),
        "status": "draft"
    }
)
if created:
    print(f"✓ فاتورة شراء: {purchase_invoice.invoice_number}")

# 11. إضافة أمر بيع
sales_order, created = SalesOrder.objects.get_or_create(
    company=company,
    branch=branch,
    order_number="SAL-ORD-001",
    defaults={
        "customer": customer_objs["Mohammed Ali"],
        "order_date": datetime.now().date(),
        "expected_delivery_date": (datetime.now() + timedelta(days=2)).date(),
        "status": "draft"
    }
)
if created:
    print(f"✓ أمر بيع: {sales_order.order_number}")

# 12. إضافة عناصر أمر البيع
for product_name, qty in [("Chocolate Cake", 10), ("Croissant", 20)]:
    SalesOrderLine.objects.get_or_create(
        sales_order=sales_order,
        product=product_objs[product_name],
        defaults={
            "quantity": Decimal(str(qty)),
            "unit_price": product_objs[product_name].selling_price,
            "discount_percent": Decimal("0"),
            "line_total": Decimal(str(qty)) * product_objs[product_name].selling_price
        }
    )
print(f"✓ عناصر أمر البيع")

# 13. إضافة فاتورة بيع
sales_invoice, created = SalesInvoice.objects.get_or_create(
    company=company,
    branch=branch,
    invoice_number="SAL-INV-001",
    defaults={
        "customer": customer_objs["Mohammed Ali"],
        "invoice_date": datetime.now().date(),
        "due_date": (datetime.now() + timedelta(days=30)).date(),
        "subtotal": Decimal("800.00"),
        "tax_amount": Decimal("80.00"),
        "discount_amount": Decimal("0.00"),
        "total_amount": Decimal("880.00"),
        "status": "draft",
        "payment_method": "cash"
    }
)
if created:
    print(f"✓ فاتورة بيع: {sales_invoice.invoice_number}")

print("\n✅ تمت إضافة جميع البيانات التجريبية بنجاح!")
print("\n📊 ملخص البيانات:")
print(f"  • شركات: {Company.objects.count()}")
print(f"  • فروع: {Branch.objects.count()}")
print(f"  • فئات: {Category.objects.count()}")
print(f"  • منتجات: {Product.objects.count()}")
print(f"  • موردين: {Supplier.objects.count()}")
print(f"  • عملاء: {Customer.objects.count()}")
print(f"  • أوامر شراء: {PurchaseOrder.objects.count()}")
print(f"  • فواتير شراء: {PurchaseInvoice.objects.count()}")
print(f"  • أوامر بيع: {SalesOrder.objects.count()}")
print(f"  • فواتير بيع: {SalesInvoice.objects.count()}")
