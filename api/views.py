from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal

from core.models import Company, Branch, Customer, Supplier, Category, Unit
from inventory.models import Product, InventoryMovement
from accounting.models import PurchaseInvoice, PurchaseOrderLine
from pos.models import SalesInvoice, POSTransaction
from manufacturing.models import Recipe, ProductionOrder

from .serializers import (
    CompanySerializer, BranchSerializer, CategorySerializer, UnitSerializer,
    CustomerSerializer, SupplierSerializer, ProductSerializer, InventoryMovementSerializer,
    PurchaseInvoiceSerializer, SalesInvoiceSerializer, POSTransactionSerializer,
    RecipeSerializer, ProductionOrderSerializer
)

class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """API للشركات"""
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.branch:
            return Company.objects.filter(id=user.branch.company.id)
        return Company.objects.none()

class BranchViewSet(viewsets.ReadOnlyModelViewSet):
    """API للفروع"""
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.branch:
            return Branch.objects.filter(company=user.branch.company)
        return Branch.objects.none()

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """API للمنتجات"""
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.branch:
            return Product.objects.filter(company=user.branch.company)
        return Product.objects.none()
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """المنتجات منخفضة المخزون"""
        user = request.user
        if not user.branch:
            return Response({'error': 'No branch assigned'}, status=status.HTTP_400_BAD_REQUEST)
        
        products = Product.objects.filter(
            company=user.branch.company,
            quantity_on_hand__lt=50
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_barcode(self, request):
        """البحث عن منتج بـ barcode"""
        barcode = request.query_params.get('barcode')
        if not barcode:
            return Response({'error': 'Barcode is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        if not user.branch:
            return Response({'error': 'No branch assigned'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(
                company=user.branch.company,
                barcode=barcode
            )
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """API للعملاء"""
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.branch:
            return Customer.objects.filter(company=user.branch.company)
        return Customer.objects.none()

class SupplierViewSet(viewsets.ReadOnlyModelViewSet):
    """API للموردين"""
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.branch:
            return Supplier.objects.filter(company=user.branch.company)
        return Supplier.objects.none()

class SalesInvoiceViewSet(viewsets.ModelViewSet):
    """API لفواتير المبيعات"""
    serializer_class = SalesInvoiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.branch:
            return SalesInvoice.objects.filter(branch=user.branch)
        return SalesInvoice.objects.none()
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """فواتير اليوم"""
        user = request.user
        if not user.branch:
            return Response({'error': 'No branch assigned'}, status=status.HTTP_400_BAD_REQUEST)
        
        today = timezone.now().date()
        invoices = SalesInvoice.objects.filter(
            branch=user.branch,
            invoice_date=today
        )
        serializer = self.get_serializer(invoices, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """إحصائيات المبيعات"""
        user = request.user
        if not user.branch:
            return Response({'error': 'No branch assigned'}, status=status.HTTP_400_BAD_REQUEST)
        
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        today_stats = SalesInvoice.objects.filter(
            branch=user.branch,
            invoice_date=today
        ).aggregate(
            total=Sum('total_amount'),
            count=Count('id')
        )
        
        month_stats = SalesInvoice.objects.filter(
            branch=user.branch,
            invoice_date__gte=month_start
        ).aggregate(
            total=Sum('total_amount'),
            count=Count('id')
        )
        
        return Response({
            'today': today_stats,
            'month': month_stats
        })

class POSTransactionViewSet(viewsets.ModelViewSet):
    """API لمعاملات نقطة البيع"""
    serializer_class = POSTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.branch:
            return POSTransaction.objects.filter(branch=user.branch)
        return POSTransaction.objects.none()

class InventoryMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """API لحركات المخزون"""
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.branch:
            return InventoryMovement.objects.filter(product__company=user.branch.company)
        return InventoryMovement.objects.none()

class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    """API للوصفات"""
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.branch:
            return Recipe.objects.filter(product__company=user.branch.company)
        return Recipe.objects.none()

class ProductionOrderViewSet(viewsets.ModelViewSet):
    """API لأوامر الإنتاج"""
    serializer_class = ProductionOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.branch:
            return ProductionOrder.objects.filter(branch=user.branch)
        return ProductionOrder.objects.none()
