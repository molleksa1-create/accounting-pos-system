from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.models import CustomUser

# تخصيص صفحة الدخول
admin.site.site_header = 'نظام المحاسبة والمخزون ونقطة البيع'
admin.site.site_title = 'إدارة النظام'
admin.site.index_title = 'مرحباً بك في لوحة التحكم'

class CustomUserAdmin(BaseUserAdmin):
    pass

# إلغاء التسجيل السابق وإعادة التسجيل
try:
    admin.site.unregister(CustomUser)
except:
    pass

admin.site.register(CustomUser, CustomUserAdmin)

