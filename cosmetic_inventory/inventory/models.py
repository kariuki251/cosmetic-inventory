from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
class Product(models.Model):
    name = models.CharField(max_length=100)
    description=models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name


    from django.db import models
from django.utils import timezone

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def _str_(self):
        return self.name


class Sale(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def _str_(self):
        return f"Sale #{self.id} - {self.date.strftime('%Y-%m-%d')}"

    # AUTO CALCULATE TOTAL
    def calculate_total(self):
        total = sum(item.subtotal() for item in self.items.all())
        self.total_amount = total
        self.save()


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price

    # AUTO UPDATE SALE TOTAL AFTER SAVE
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sale.calculate_total()

    # AUTO UPDATE SALE TOTAL AFTER DELETE
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.sale.calculate_total()

    from django.db import models
    from django.db import models

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def _str_(self):
        return self.name

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('stock', 'Stock Purchase'),
        ('utilities', 'Utilities'),
        ('salary', 'Salary'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ]

    description = models.CharField(max_length=255, null=True, blank=True)
    category = models.ForeignKey(ExpenseCategory,on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.description} - KSh {self.amount}"