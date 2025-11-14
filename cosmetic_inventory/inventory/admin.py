from django.contrib import admin

# Register your models here.
from .models import Product, Customer, Sale, SaleItem, Category, Expense, ExpenseCategory

admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Sale)
admin.site.register(SaleItem)
admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(ExpenseCategory)