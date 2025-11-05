@echo off
REM =====================================================
REM نظام المحاسبة والمخزون ونقطة البيع - برنامج التثبيت
REM =====================================================

echo.
echo ========================================
echo   نظام المحاسبة والمخزون ونقطة البيع
echo   برنامج التثبيت التلقائي
echo ========================================
echo.

REM التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [خطأ] Python غير مثبت على النظام!
    echo يرجى تثبيت Python 3.11 أو أحدث من https://www.python.org
    pause
    exit /b 1
)

echo [✓] تم التحقق من Python

REM إنشاء بيئة افتراضية إذا لم تكن موجودة
if not exist "venv" (
    echo.
    echo [جاري] إنشاء بيئة افتراضية...
    python -m venv venv
    echo [✓] تم إنشاء البيئة الافتراضية
) else (
    echo [✓] البيئة الافتراضية موجودة بالفعل
)

REM تفعيل البيئة الافتراضية
echo.
echo [جاري] تفعيل البيئة الافتراضية...
call venv\Scripts\activate.bat
echo [✓] تم تفعيل البيئة الافتراضية

REM تثبيت المكتبات
echo.
echo [جاري] تثبيت المكتبات المطلوبة...
echo هذا قد يستغرق بعض الوقت...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [خطأ] فشل تثبيت المكتبات!
    pause
    exit /b 1
)
echo [✓] تم تثبيت جميع المكتبات بنجاح

REM تطبيق الهجرات
echo.
echo [جاري] تطبيق هجرات قاعدة البيانات...
python manage.py migrate --quiet
if errorlevel 1 (
    echo [خطأ] فشل تطبيق الهجرات!
    pause
    exit /b 1
)
echo [✓] تم تطبيق الهجرات بنجاح

REM جمع الملفات الثابتة
echo.
echo [جاري] جمع الملفات الثابتة...
python manage.py collectstatic --noinput --quiet 2>nul
echo [✓] تم جمع الملفات الثابتة

REM تشغيل السيرفر
echo.
echo ========================================
echo   [✓] تم إعداد البرنامج بنجاح!
echo ========================================
echo.
echo [معلومة] سيتم فتح البرنامج في المتصفح...
echo [معلومة] الرابط: http://localhost:8000
echo.
echo [تنبيه] لا تغلق هذه النافذة أثناء استخدام البرنامج
echo [تنبيه] لإيقاف البرنامج: اضغط CTRL + C
echo.

REM فتح المتصفح
timeout /t 2 /nobreak >nul
start http://localhost:8000

REM تشغيل السيرفر
python manage.py runserver

pause

