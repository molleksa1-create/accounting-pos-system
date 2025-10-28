from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet, basename='company')
router.register(r'branches', views.BranchViewSet, basename='branch')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'suppliers', views.SupplierViewSet, basename='supplier')
router.register(r'sales-invoices', views.SalesInvoiceViewSet, basename='sales-invoice')
router.register(r'pos-transactions', views.POSTransactionViewSet, basename='pos-transaction')
router.register(r'inventory-movements', views.InventoryMovementViewSet, basename='inventory-movement')
router.register(r'recipes', views.RecipeViewSet, basename='recipe')
router.register(r'production-orders', views.ProductionOrderViewSet, basename='production-order')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
]
