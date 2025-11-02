from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from core.models import CustomUser

class AutoLoginMiddleware:
    """
    Middleware لتسجيل الدخول التلقائي للمستخدم admin
    يسمح بفتح النظام بدون طلب بيانات دخول
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # إذا كان المستخدم غير مسجل دخول
        if not request.user.is_authenticated:
            try:
                # حاول الدخول التلقائي بـ admin
                user = CustomUser.objects.get(username='admin')
                request.user = user
            except CustomUser.DoesNotExist:
                # إذا لم يوجد admin، حاول إنشاؤه
                try:
                    user = CustomUser.objects.create_superuser(
                        username='admin',
                        email='admin@example.com',
                        password='admin123'
                    )
                    request.user = user
                except:
                    pass
        
        response = self.get_response(request)
        return response

