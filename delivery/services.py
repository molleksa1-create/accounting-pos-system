import requests
import json
from django.conf import settings
from .models import DeliveryOrder, DeliveryPlatform, DeliveryIntegrationLog, DeliveryTracking

class DeliveryPlatformService:
    """خدمة التكامل مع منصات التوصيل"""
    
    def __init__(self, platform: DeliveryPlatform):
        self.platform = platform
        self.api_key = platform.api_key
        self.api_secret = platform.api_secret
    
    def create_order(self, delivery_order: DeliveryOrder):
        """إنشاء طلب توصيل على المنصة"""
        if self.platform.platform_name == 'hanger':
            return self._create_hanger_order(delivery_order)
        elif self.platform.platform_name == 'kita':
            return self._create_kita_order(delivery_order)
        else:
            raise ValueError(f"منصة غير مدعومة: {self.platform.platform_name}")
    
    def _create_hanger_order(self, delivery_order: DeliveryOrder):
        """إنشاء طلب على Hanger Station"""
        url = "https://api.hanger.sa/v1/orders"
        
        payload = {
            "customer_name": delivery_order.customer.name if delivery_order.customer else "عميل",
            "customer_phone": delivery_order.delivery_phone,
            "delivery_address": delivery_order.delivery_address,
            "items": self._format_items(delivery_order),
            "notes": delivery_order.delivery_notes,
            "total_amount": float(delivery_order.sales_invoice.total_amount),
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            # حفظ سجل التكامل
            DeliveryIntegrationLog.objects.create(
                platform=self.platform,
                action='create_order',
                request_data=payload,
                response_data=result,
                status_code=response.status_code,
                is_success=True
            )
            
            # تحديث رقم الطلب على المنصة
            delivery_order.platform_order_id = result.get('order_id')
            delivery_order.status = 'confirmed'
            delivery_order.save()
            
            return {'success': True, 'order_id': result.get('order_id')}
        
        except Exception as e:
            DeliveryIntegrationLog.objects.create(
                platform=self.platform,
                action='create_order',
                request_data=payload,
                response_data={},
                error_message=str(e),
                is_success=False
            )
            return {'success': False, 'error': str(e)}
    
    def _create_kita_order(self, delivery_order: DeliveryOrder):
        """إنشاء طلب على Kita"""
        url = "https://api.kita.sa/v1/orders"
        
        payload = {
            "merchant_id": self.api_key,
            "customer_name": delivery_order.customer.name if delivery_order.customer else "عميل",
            "customer_phone": delivery_order.delivery_phone,
            "delivery_address": delivery_order.delivery_address,
            "items": self._format_items(delivery_order),
            "notes": delivery_order.delivery_notes,
            "total_amount": float(delivery_order.sales_invoice.total_amount),
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_secret}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            # حفظ سجل التكامل
            DeliveryIntegrationLog.objects.create(
                platform=self.platform,
                action='create_order',
                request_data=payload,
                response_data=result,
                status_code=response.status_code,
                is_success=True
            )
            
            # تحديث رقم الطلب على المنصة
            delivery_order.platform_order_id = result.get('order_id')
            delivery_order.status = 'confirmed'
            delivery_order.save()
            
            return {'success': True, 'order_id': result.get('order_id')}
        
        except Exception as e:
            DeliveryIntegrationLog.objects.create(
                platform=self.platform,
                action='create_order',
                request_data=payload,
                response_data={},
                error_message=str(e),
                is_success=False
            )
            return {'success': False, 'error': str(e)}
    
    def update_order_status(self, delivery_order: DeliveryOrder, status: str):
        """تحديث حالة الطلب"""
        if self.platform.platform_name == 'hanger':
            return self._update_hanger_status(delivery_order, status)
        elif self.platform.platform_name == 'kita':
            return self._update_kita_status(delivery_order, status)
    
    def _update_hanger_status(self, delivery_order: DeliveryOrder, status: str):
        """تحديث حالة الطلب على Hanger"""
        url = f"https://api.hanger.sa/v1/orders/{delivery_order.platform_order_id}"
        
        payload = {"status": status}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = requests.patch(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            # تحديث حالة الطلب محلياً
            delivery_order.status = status
            delivery_order.save()
            
            # حفظ تتبع
            DeliveryTracking.objects.create(
                delivery_order=delivery_order,
                status=status
            )
            
            return {'success': True}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _update_kita_status(self, delivery_order: DeliveryOrder, status: str):
        """تحديث حالة الطلب على Kita"""
        url = f"https://api.kita.sa/v1/orders/{delivery_order.platform_order_id}"
        
        payload = {"status": status}
        headers = {"Authorization": f"Bearer {self.api_secret}"}
        
        try:
            response = requests.patch(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            # تحديث حالة الطلب محلياً
            delivery_order.status = status
            delivery_order.save()
            
            # حفظ تتبع
            DeliveryTracking.objects.create(
                delivery_order=delivery_order,
                status=status
            )
            
            return {'success': True}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def cancel_order(self, delivery_order: DeliveryOrder):
        """إلغاء طلب التوصيل"""
        if self.platform.platform_name == 'hanger':
            return self._cancel_hanger_order(delivery_order)
        elif self.platform.platform_name == 'kita':
            return self._cancel_kita_order(delivery_order)
    
    def _cancel_hanger_order(self, delivery_order: DeliveryOrder):
        """إلغاء طلب على Hanger"""
        url = f"https://api.hanger.sa/v1/orders/{delivery_order.platform_order_id}/cancel"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = requests.post(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            delivery_order.status = 'cancelled'
            delivery_order.save()
            
            return {'success': True}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _cancel_kita_order(self, delivery_order: DeliveryOrder):
        """إلغاء طلب على Kita"""
        url = f"https://api.kita.sa/v1/orders/{delivery_order.platform_order_id}/cancel"
        headers = {"Authorization": f"Bearer {self.api_secret}"}
        
        try:
            response = requests.post(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            delivery_order.status = 'cancelled'
            delivery_order.save()
            
            return {'success': True}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _format_items(delivery_order: DeliveryOrder):
        """تنسيق عناصر الطلب"""
        items = []
        for item in delivery_order.sales_invoice.items.all():
            items.append({
                'name': item.product.name_ar,
                'quantity': item.quantity,
                'price': float(item.unit_price),
                'total': float(item.total_amount)
            })
        return items
