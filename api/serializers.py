from rest_framework import serializers
from core.models import Company, Branch, Customer, Supplier, Category, Unit
from inventory.models import Product, InventoryMovement
from accounting.models import PurchaseOrder, PurchaseInvoice, PurchaseOrderLine
from pos.models import SalesOrder, SalesInvoice, POSTransaction
from manufacturing.models import Recipe, ProductionOrder

# Core Serializers
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name_ar', 'name_en', 'tax_id', 'phone', 'email']

class BranchSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    
    class Meta:
        model = Branch
        fields = ['id', 'company', 'name_ar', 'name_en', 'address', 'phone', 'email']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name_ar', 'name_en', 'code', 'description']

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name_ar', 'name_en', 'code']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'address', 'city', 'balance']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name_ar', 'name_en', 'email', 'phone', 'address', 'city', 'balance']

# Inventory Serializers
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    unit = UnitSerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'code', 'name_ar', 'name_en', 'barcode', 'category', 'unit', 
                  'cost_price', 'selling_price', 'quantity_on_hand', 'is_active']

class InventoryMovementSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = InventoryMovement
        fields = ['id', 'product', 'movement_type', 'quantity', 'reference_number', 'notes', 'created_at']

# Accounting Serializers
class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = PurchaseOrderLine
        fields = ['id', 'product', 'quantity', 'unit_price', 'line_total']

class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(read_only=True)
    
    class Meta:
        model = PurchaseInvoice
        fields = ['id', 'invoice_number', 'supplier', 'invoice_date', 'due_date', 
                  'status', 'total_amount', 'notes']

# POS Serializers
class SalesInvoiceSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    
    class Meta:
        model = SalesInvoice
        fields = ['id', 'invoice_number', 'customer', 'invoice_date', 'status', 
                  'total_amount', 'notes']

class POSTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = POSTransaction
        fields = ['id', 'transaction_type', 'amount', 'payment_method', 'reference_number', 'created_at']

# Manufacturing Serializers
class RecipeSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = Recipe
        fields = ['id', 'product', 'name_ar', 'name_en', 'description', 'yield_quantity']

class ProductionOrderSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)
    
    class Meta:
        model = ProductionOrder
        fields = ['id', 'recipe', 'quantity', 'status', 'scheduled_date', 'completed_date']
