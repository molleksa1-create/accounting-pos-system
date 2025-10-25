# وثيقة البنية المعمارية (Architecture Documentation)

## 1. نظرة عامة على النظام

نظام محاسبي متكامل مفتوح المصدر يجمع بين:
- **إدارة المشتريات والموردين**: تتبع كامل لأوامر الشراء والفواتير
- **نظام المخزون المتقدم**: إدارة المنتجات والمواد الخام مع حركات تفصيلية
- **نظام التصنيع والوصفات**: تحديد الوصفات وأوامر الإنتاج
- **نظام المبيعات والفواتير**: إدارة العملاء والفواتير
- **نقطة البيع (POS)**: واجهة كاشير سهلة الاستخدام
- **التقارير والتحليلات**: تقارير شاملة ولوحة تحكم
- **إدارة المستخدمين والأدوار**: نظام صلاحيات متقدم

## 2. البنية التقنية

### المكدس التقني (Tech Stack)

| المكون | التقنية | السبب |
|-------|--------|------|
| **الواجهة الخلفية** | Django 5.2 | إطار عمل قوي وآمن مع ORM ممتاز |
| **API** | Django REST Framework | بناء APIs قوية وموثقة |
| **قاعدة البيانات** | PostgreSQL | قاعدة بيانات موثوقة وقوية |
| **الواجهة الأمامية** | HTML/CSS/JavaScript | واجهة بسيطة وسريعة |
| **تطبيق الأندرويد** | React Native/Flutter | تطوير سريع لمنصات متعددة |
| **المصادقة** | Session-based + Token | أمان عالي |

### البنية الهندسية

```
accounting_pos_system/
│
├── config/                          # إعدادات المشروع
│   ├── settings.py                 # إعدادات Django
│   ├── urls.py                     # توجيه URLs
│   ├── wsgi.py                     # WSGI application
│   └── asgi.py                     # ASGI application
│
├── core/                            # التطبيق الأساسي
│   ├── models.py                   # نماذج المستخدمين والشركات
│   ├── views.py                    # عروض المستخدمين
│   ├── serializers.py              # محولات البيانات
│   ├── urls.py                     # توجيه URLs
│   └── admin.py                    # لوحة التحكم الإدارية
│
├── inventory/                       # إدارة المخزون
│   ├── models.py                   # نماذج المنتجات والمخزون
│   ├── views.py                    # عروض المخزون
│   ├── serializers.py              # محولات بيانات المخزون
│   ├── urls.py                     # توجيه URLs
│   └── admin.py                    # إدارة المخزون
│
├── manufacturing/                   # نظام التصنيع
│   ├── models.py                   # نماذج الوصفات والإنتاج
│   ├── views.py                    # عروض الإنتاج
│   ├── serializers.py              # محولات بيانات الإنتاج
│   ├── urls.py                     # توجيه URLs
│   └── admin.py                    # إدارة الإنتاج
│
├── accounting/                      # المحاسبة والفواتير
│   ├── models.py                   # نماذج الفواتير والمشتريات
│   ├── views.py                    # عروض المحاسبة
│   ├── serializers.py              # محولات بيانات المحاسبة
│   ├── urls.py                     # توجيه URLs
│   └── admin.py                    # إدارة المحاسبة
│
├── pos/                             # نقطة البيع
│   ├── models.py                   # نماذج نقطة البيع
│   ├── views.py                    # عروض نقطة البيع
│   ├── serializers.py              # محولات بيانات POS
│   ├── urls.py                     # توجيه URLs
│   └── admin.py                    # إدارة POS
│
├── reports/                         # التقارير والتحليلات
│   ├── models.py                   # نماذج التقارير
│   ├── views.py                    # عروض التقارير
│   ├── serializers.py              # محولات بيانات التقارير
│   ├── urls.py                     # توجيه URLs
│   └── admin.py                    # إدارة التقارير
│
├── templates/                       # قوالب HTML
│   ├── base.html                   # القالب الأساسي
│   ├── dashboard.html              # لوحة التحكم
│   ├── inventory/                  # قوالب المخزون
│   ├── accounting/                 # قوالب المحاسبة
│   ├── pos/                        # قوالب نقطة البيع
│   └── reports/                    # قوالب التقارير
│
├── static/                          # ملفات ثابتة
│   ├── css/                        # ملفات CSS
│   ├── js/                         # ملفات JavaScript
│   └── images/                     # صور
│
├── media/                           # ملفات المستخدمين
│   ├── products/                   # صور المنتجات
│   ├── companies/                  # شعارات الشركات
│   └── uploads/                    # ملفات أخرى
│
├── manage.py                        # أداة إدارة Django
├── requirements.txt                 # المكتبات المطلوبة
├── .env                            # متغيرات البيئة
├── .gitignore                      # ملفات Git المتجاهلة
└── README.md                       # ملف التوثيق الرئيسي
```

## 3. نماذج البيانات (Data Models)

### 3.1 نموذج المستخدم (CustomUser)

```python
CustomUser
├── id (UUID)
├── username
├── email
├── password
├── first_name
├── last_name
├── phone
├── role (admin, manager, accountant, cashier, warehouse, viewer)
├── branch (FK)
├── is_active
├── created_at
└── updated_at
```

### 3.2 نموذج الشركة والفروع

```python
Company
├── id (UUID)
├── name
├── name_ar
├── logo
├── email
├── phone
├── address
├── tax_id
├── commercial_register
├── currency
└── branches (Reverse FK)

Branch
├── id (UUID)
├── company (FK)
├── name
├── name_ar
├── code
├── address
├── is_main_branch
├── opening_balance
└── users (Reverse FK)
```

### 3.3 نموذج المنتج والمخزون

```python
Product
├── id (UUID)
├── company (FK)
├── name
├── code
├── barcode
├── category (FK)
├── unit (FK)
├── cost_price
├── selling_price
├── quantity_on_hand
├── reorder_level
├── reorder_quantity
└── is_active

InventoryMovement
├── id (UUID)
├── product (FK)
├── branch (FK)
├── movement_type
├── quantity
├── unit_price
├── reference_type
├── reference_id
└── created_at

StockLevel
├── id (UUID)
├── product (FK)
├── branch (FK)
├── quantity
├── last_counted_at
└── updated_at
```

### 3.4 نموذج الوصفة والإنتاج

```python
Recipe
├── id (UUID)
├── company (FK)
├── name
├── code
├── product (FK)
├── output_quantity
├── production_time_minutes
└── ingredients (Reverse FK)

RecipeIngredient
├── id (UUID)
├── recipe (FK)
├── product (FK)
├── quantity
├── unit (FK)
└── is_main_ingredient

ProductionOrder
├── id (UUID)
├── company (FK)
├── branch (FK)
├── order_number
├── recipe (FK)
├── planned_quantity
├── produced_quantity
├── status
├── planned_start_date
├── actual_start_date
└── lines (Reverse FK)
```

### 3.5 نموذج الفواتير والمشتريات

```python
PurchaseOrder
├── id (UUID)
├── company (FK)
├── branch (FK)
├── order_number
├── supplier (FK)
├── order_date
├── status
├── subtotal
├── tax_amount
├── total_amount
└── lines (Reverse FK)

PurchaseInvoice
├── id (UUID)
├── company (FK)
├── branch (FK)
├── invoice_number
├── supplier (FK)
├── invoice_date
├── due_date
├── total_amount
├── paid_amount
├── status
└── payment_method

SalesInvoice
├── id (UUID)
├── company (FK)
├── branch (FK)
├── invoice_number
├── customer (FK)
├── invoice_date
├── total_amount
├── paid_amount
├── status
└── payment_method
```

### 3.6 نموذج نقطة البيع

```python
POSSession
├── id (UUID)
├── branch (FK)
├── cashier (FK)
├── opening_balance
├── closing_balance
├── status
├── opened_at
└── closed_at

POSTransaction
├── id (UUID)
├── session (FK)
├── invoice (FK)
├── quantity
├── unit_price
├── total_amount
└── transaction_date
```

## 4. تدفق البيانات (Data Flow)

### 4.1 تدفق عملية الشراء

```
1. إنشاء أمر شراء (PurchaseOrder)
   ↓
2. إضافة أسطر الأمر (PurchaseOrderLine)
   ↓
3. تأكيد الأمر
   ↓
4. استقبال البضائع (GoodsReceipt)
   ↓
5. تحديث مستوى المخزون (StockLevel)
   ↓
6. إنشاء حركة مخزون (InventoryMovement)
   ↓
7. استقبال فاتورة (PurchaseInvoice)
   ↓
8. تسجيل الدفع
```

### 4.2 تدفق عملية البيع

```
1. إنشاء أمر بيع (SalesOrder)
   ↓
2. إضافة أسطر الأمر (SalesOrderLine)
   ↓
3. إنشاء فاتورة (SalesInvoice)
   ↓
4. تحديث مستوى المخزون (StockLevel)
   ↓
5. إنشاء حركة مخزون (InventoryMovement)
   ↓
6. تسجيل الدفع
   ↓
7. إغلاق الفاتورة
```

### 4.3 تدفق عملية الإنتاج

```
1. إنشاء أمر إنتاج (ProductionOrder)
   ↓
2. إضافة أسطر الأمر مع المكونات
   ↓
3. بدء الإنتاج
   ↓
4. تسجيل المواد المستهلكة
   ↓
5. تحديث مستويات المخزون
   ↓
6. إنشاء حركات مخزون للمواد الخام والمنتجات النهائية
   ↓
7. إغلاق أمر الإنتاج
```

## 5. نظام الأدوار والصلاحيات (RBAC)

### الأدوار المتاحة

| الدور | الصلاحيات |
|------|----------|
| **مسؤول النظام** | وصول كامل لجميع الميزات والإعدادات |
| **مدير** | إدارة الفروع والمستخدمين والتقارير |
| **محاسب** | إدارة الفواتير والمشتريات والتقارير المالية |
| **كاشير** | نقطة البيع والمبيعات فقط |
| **أمين مخزن** | إدارة المخزون والحركات |
| **عارض بيانات** | عرض البيانات والتقارير فقط (بدون تعديل) |

## 6. API Endpoints (نقاط نهاية API)

### المستخدمين والمصادقة
- `POST /api/auth/login/` - تسجيل الدخول
- `POST /api/auth/logout/` - تسجيل الخروج
- `GET /api/users/` - قائمة المستخدمين
- `POST /api/users/` - إنشاء مستخدم جديد

### المنتجات والمخزون
- `GET /api/products/` - قائمة المنتجات
- `POST /api/products/` - إنشاء منتج
- `GET /api/inventory/movements/` - حركات المخزون
- `POST /api/inventory/movements/` - إنشاء حركة مخزون

### الفواتير والمشتريات
- `GET /api/purchase-orders/` - قائمة أوامر الشراء
- `POST /api/purchase-orders/` - إنشاء أمر شراء
- `GET /api/sales-invoices/` - قائمة فواتير البيع
- `POST /api/sales-invoices/` - إنشاء فاتورة بيع

### التقارير
- `GET /api/reports/sales/` - تقرير المبيعات
- `GET /api/reports/inventory/` - تقرير المخزون
- `GET /api/reports/financial/` - التقرير المالي

## 7. قاعدة البيانات

### الاتصال

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'accounting_pos',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### الهجرات (Migrations)

```bash
python manage.py makemigrations
python manage.py migrate
```

## 8. الأمان (Security)

- ✅ CSRF Protection
- ✅ SQL Injection Prevention (ORM)
- ✅ XSS Protection
- ✅ CORS Configuration
- ✅ Password Hashing
- ✅ Session Management
- ✅ Audit Logging

## 9. الأداء (Performance)

- ✅ Database Indexing
- ✅ Query Optimization
- ✅ Pagination
- ✅ Caching Strategy
- ✅ Async Tasks (Celery)

## 10. التوسعية (Scalability)

- ✅ Modular Architecture
- ✅ Microservices Ready
- ✅ Multi-tenant Support
- ✅ Multi-branch Support
- ✅ API-First Design

---

**آخر تحديث**: 25 أكتوبر 2025  
**الإصدار**: 1.0.0  
**الحالة**: قيد التطوير

