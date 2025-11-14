from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<int:id>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:id>/delete/', views.delete_product, name='delete_product'),
    path('sales/', views.sale_list,
         name='sale_list'),
    path('sales/edit/<int:sale_id>/',
         views.edit_sale, name='edit_sale'),
    path('sales/delete/<int:sale_id>/',
         views.delete_sale, name='delete_sale'),
    path('sales/add/', views.add_sale, name='add_sale'),


    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('expenses/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    ]
