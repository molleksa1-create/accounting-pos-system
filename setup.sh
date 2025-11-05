#!/bin/bash

# =====================================================
# نظام المحاسبة والمخزون ونقطة البيع - برنامج التثبيت
# =====================================================

echo ""
echo "========================================"
echo "  نظام المحاسبة والمخزون ونقطة البيع"
echo "  برنامج التثبيت التلقائي"
echo "========================================"
echo ""

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "[خطأ] Python3 غير مثبت على النظام!"
    echo "يرجى تثبيت Python 3.11 أو أحدث"
    exit 1
fi

echo "[✓] تم التحقق من Python"

# إنشاء بيئة افتراضية إذا لم تكن موجودة
if [ ! -d "venv" ]; then
    echo ""
    echo "[جاري] إنشاء بيئة افتراضية..."
    python3 -m venv venv
    echo "[✓] تم إنشاء البيئة الافتراضية"
else
    echo "[✓] البيئة الافتراضية موجودة بالفعل"
fi

# تفعيل البيئة الافتراضية
echo ""
echo "[جاري] تفعيل البيئة الافتراضية..."
source venv/bin/activate
echo "[✓] تم تفعيل البيئة الافتراضية"

# تثبيت المكتبات
echo ""
echo "[جاري] تثبيت المكتبات المطلوبة..."
echo "هذا قد يستغرق بعض الوقت..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "[خطأ] فشل تثبيت المكتبات!"
    exit 1
fi
echo "[✓] تم تثبيت جميع المكتبات بنجاح"

# تطبيق الهجرات
echo ""
echo "[جاري] تطبيق هجرات قاعدة البيانات..."
python manage.py migrate --quiet
if [ $? -ne 0 ]; then
    echo "[خطأ] فشل تطبيق الهجرات!"
    exit 1
fi
echo "[✓] تم تطبيق الهجرات بنجاح"

# جمع الملفات الثابتة
echo ""
echo "[جاري] جمع الملفات الثابتة..."
python manage.py collectstatic --noinput --quiet 2>/dev/null
echo "[✓] تم جمع الملفات الثابتة"

# تشغيل السيرفر
echo ""
echo "========================================"
echo "  [✓] تم إعداد البرنامج بنجاح!"
echo "========================================"
echo ""
echo "[معلومة] سيتم فتح البرنامج في المتصفح..."
echo "[معلومة] الرابط: http://localhost:8000"
echo ""
echo "[تنبيه] لا تغلق هذه النافذة أثناء استخدام البرنامج"
echo "[تنبيه] لإيقاف البرنامج: اضغط CTRL + C"
echo ""

# فتح المتصفح (إذا كان متاحاً)
sleep 2
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8000 &
elif command -v open &> /dev/null; then
    open http://localhost:8000 &
fi

# تشغيل السيرفر
python manage.py runserver

