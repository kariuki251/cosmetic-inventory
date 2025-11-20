from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Expense, ExpenseCategory

def dashboard(request):
    products = Product.objects.all()
    return render(request, 'inventory/dashboard.html', {'products': products})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

@login_required
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        quantity = request.POST.get('quantity',0)
        price = request.POST.get('price',0)
        Product.objects.create(name=name, quantity=quantity, price=price)
        return redirect('product_list')
    
    return render(request, 'inventory/add_product.html')
@login_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()

    if request.method == 'POST':
        product.name = request.POST.get('name', product.name)
        product.quantity = request.POST.get('quantity', product.quantity)
        product.price = request.POST.get('price', product.price)
        product.save()
        return redirect('product_list')

    return render(request, 'inventory/edit_product.html', {'product': product})
@login_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect('product_list')


from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.utils import timezone
from .models import Product, Sale, SaleItem, Customer
import datetime


# --------------------------
# ADD SALE
# --------------------------
@login_required
def add_sale(request):
    products = Product.objects.all()

    if request.method == 'POST':

        sale = Sale.objects.create()

        for product in products:
            qty__str = request.POST.get(f'qty_{product.id}' ,'0')
            try:qty = int(qty__str) 
            except ValueError: qty=0

            if qty > 0:
                price = product.price
                if product.price is None:
                    product.price = 0.0
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty,
                    price=price
                )

                # reduce stock
                product.quantity -= qty
                product.save()

        sale.calculate_total()
        return redirect('sale_list')

    return render(request, 'inventory/add_sale.html', {
        'products': products,
        
    })

# --------------------------
# EDIT SALE
# --------------------------
@login_required
def edit_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    products = Product.objects.all()

    if request.method == 'POST':
        # Update quantities of existing items
        for item in sale.items.all():
            new_qty = int(request.POST.get(f'qty_{item.product.id}', item.quantity))

            # Adjust stock accordingly
            stock_change = item.quantity - new_qty
            item.product.quantity += stock_change
            item.product.save()

            # Update item
            item.quantity = new_qty
            item.price = item.product.price  # in case price changed
            item.save()  # This will auto-calc total

        sale.calculate_total()
        return redirect('sale_list')

    return render(request, 'inventory/edit_sale.html', {
        'sale': sale,
        'products': products
    })

# --------------------------
# DELETE SALE
# --------------------------
@login_required
def delete_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)

    # Return items to stock before deleting
    for item in sale.items.all():
        item.product.quantity += item.quantity
        item.product.save()

    sale.delete()
    return redirect('sale_list')

# --------------------------
# SALE LIST
# --------------------------
def sale_list(request):
    sales = Sale.objects.all().order_by('-date')
    return render(request, 'inventory/sale_list.html', {'sales': sales})



from django.shortcuts import render, get_object_or_404, redirect
from .models import Expense, ExpenseCategory

# 📋 List all expenses
def expense_list(request):
    expenses = Expense.objects.all().order_by('-date')
    return render(request, 'inventory/expense_list.html', {'expenses': expenses})

# ➕ Add expense
def add_expense(request):
    categories = ExpenseCategory.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('category')
        category = ExpenseCategory.objects.get(id=category_id) if category_id else None
        description = request.POST.get('description')
        amount = request.POST.get('amount')

        Expense.objects.create(
            category=category,
            description=description,
            amount=amount
        )
        return redirect('expense_list')

    return render(request, 'inventory/add_expense.html', {'categories': categories})

# ✏ Edit expense
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    categories = ExpenseCategory.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('category')
        expense.category = ExpenseCategory.objects.get(id=category_id) if category_id else None
        expense.description = request.POST.get('description')
        expense.amount = request.POST.get('amount')
        expense.save()
        return redirect('expense_list')

    return render(request, 'inventory/edit_expense.html', {'expense': expense, 'categories': categories})

# ❌ Delete expense
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    return render(request, 'inventory/delete_expense.html', {'expense': expense})

from django.shortcuts import render, redirect, get_object_or_404
from .models import ExpenseCategory, Expense

# List all categories
def expense_category_list(request):
    categories = ExpenseCategory.objects.all().order_by('name')
    return render(request, 'inventory/expense_category_list.html', {'categories': categories})

# Add a new category
def add_expense_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            ExpenseCategory.objects.create(name=name)
            return redirect('expense_category_list')
    return render(request, 'inventory/add_expense_category.html')

# Edit a category
def edit_expense_category(request, category_id):
    category = get_object_or_404(ExpenseCategory, id=category_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            category.name = name
            category.save()
            return redirect('expense_category_list')
    return render(request, 'inventory/edit_expense_category.html', {'category': category})

# Delete a category
def delete_expense_category(request, category_id):
    category = get_object_or_404(ExpenseCategory, id=category_id)
    category.delete()
    return redirect('expense_category_list')

from .models import Product, Sale, Expense, ExpenseCategory
from django.db.models import Sum

def dashboard(request):
    # Products count
    total_products = Product.objects.count()
    
    # Sales total
    total_sales = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0

    # Expenses total
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0

    # Profit (Sales - Expenses)
    profit = total_sales - total_expenses

    # Top products by quantity sold
    top_products = Product.objects.order_by('-quantity')[:5]

    # Expense breakdown by category
    expense_breakdown = (
        Expense.objects.values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    context = {
        'total_products': total_products,
        'total_sales': total_sales,
        'total_expenses': total_expenses,
        'profit': profit,
        'top_products': top_products,
        'expense_breakdown': expense_breakdown,
    }

    return render(request, 'inventory/dashboard.html', context)