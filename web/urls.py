from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.products_list, name='products_list'),
    path('sales-report/', views.sales_report, name='sales_report'),
    path('inventory-report/', views.inventory_report, name='inventory_report'),
]
