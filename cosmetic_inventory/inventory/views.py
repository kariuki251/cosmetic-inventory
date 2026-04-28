from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum
from .models import (
    Product, Category,
    Sale, SaleItem,
    Expense, ExpenseCategory
)


# ==========================
# DASHBOARD
# ==========================
def dashboard(request):
    total_products = Product.objects.count()
    total_sales = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    profit = total_sales - total_expenses

    top_products = Product.objects.order_by('-quantity')[:5]

    expense_breakdown = (
        Expense.objects.values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    return render(request, 'inventory/dashboard.html', {
        'total_products': total_products,
        'total_sales': total_sales,
        'total_expenses': total_expenses,
        'profit': profit,
        'top_products': top_products,
        'expense_breakdown': expense_breakdown,
    })


# ==========================
# PRODUCTS
# ==========================
def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})


def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        quantity = int(request.POST.get('quantity', 0) or 0)
        price = float(request.POST.get('price', 0) or 0)

        Product.objects.create(name=name, quantity=quantity, price=price)

        # Instead of redirect, reload page with success message
        return render(request, 'inventory/add_product.html', {'message': 'Product added'})

    return render(request, 'inventory/add_product.html')


def edit_product(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return HttpResponse("Product not found")

    if request.method == 'POST':
        product.name = request.POST.get('name', product.name)
        product.quantity = int(request.POST.get('quantity', product.quantity) or product.quantity)
        product.price = float(request.POST.get('price', product.price) or product.price)
        product.save()

        return render(request, 'inventory/edit_product.html', {
            'product': product,
            'message': 'Product updated'
        })

    return render(request, 'inventory/edit_product.html', {'product': product})


def delete_product(request, id):
    try:
        product = Product.objects.get(id=id)
        product.delete()
        return render(request, 'inventory/product_list.html', {
            'products': Product.objects.all(),
            'message': 'Product deleted'
        })
    except Product.DoesNotExist:
        return HttpResponse("Product not found")


# ==========================
# SALES
# ==========================
def sale_list(request):
    sales = Sale.objects.all().order_by('-date')
    return render(request, 'inventory/sale_list.html', {'sales': sales})


def add_sale(request):
    products = Product.objects.all()

    if request.method == 'POST':
        sale = Sale.objects.create()

        for product in products:
            qty = int(request.POST.get(f'qty_{product.id}', 0) or 0)

            if qty > 0:
                price = product.price or 0

                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty,
                    price=price
                )

                product.quantity -= qty
                product.save()

        sale.calculate_total()

        return render(request, 'inventory/add_sale.html', {
            'products': products,
            'message': 'Sale added'
        })

    return render(request, 'inventory/add_sale.html', {'products': products})


def edit_sale(request, sale_id):
    try:
        sale = Sale.objects.get(id=sale_id)
    except Sale.DoesNotExist:
        return HttpResponse("Sale not found")

    products = Product.objects.all()

    if request.method == 'POST':
        for item in sale.items.all():
            new_qty = int(request.POST.get(f'qty_{item.product.id}', item.quantity))

            stock_change = item.quantity - new_qty
            item.product.quantity += stock_change
            item.product.save()

            item.quantity = new_qty
            item.price = item.product.price or 0
            item.save()

        sale.calculate_total()

        return render(request, 'inventory/edit_sale.html', {
            'sale': sale,
            'products': products,
            'message': 'Sale updated'
        })

    return render(request, 'inventory/edit_sale.html', {
        'sale': sale,
        'products': products
    })


def delete_sale(request, sale_id):
    try:
        sale = Sale.objects.get(id=sale_id)
    except Sale.DoesNotExist:
        return HttpResponse("Sale not found")

    for item in sale.items.all():
        item.product.quantity += item.quantity
        item.product.save()

    sale.delete()

    return render(request, 'inventory/sale_list.html', {
        'sales': Sale.objects.all(),
        'message': 'Sale deleted'
    })


# ==========================
# EXPENSES
# ==========================
def expense_list(request):
    expenses = Expense.objects.all().order_by('-date')
    return render(request, 'inventory/expense_list.html', {'expenses': expenses})


def add_expense(request):
    categories = ExpenseCategory.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('category')
        category = ExpenseCategory.objects.get(id=category_id) if category_id else None

        description = request.POST.get('description')
        amount = float(request.POST.get('amount', 0) or 0)

        Expense.objects.create(
            category=category,
            description=description,
            amount=amount
        )

        return render(request, 'inventory/add_expense.html', {
            'categories': categories,
            'message': 'Expense added'
        })

    return render(request, 'inventory/add_expense.html', {'categories': categories})


def edit_expense(request, expense_id):
    try:
        expense = Expense.objects.get(id=expense_id)
    except Expense.DoesNotExist:
        return HttpResponse("Expense not found")

    categories = ExpenseCategory.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('category')
        expense.category = ExpenseCategory.objects.get(id=category_id) if category_id else None
        expense.description = request.POST.get('description')
        expense.amount = float(request.POST.get('amount', 0) or 0)
        expense.save()

        return render(request, 'inventory/edit_expense.html', {
            'expense': expense,
            'categories': categories,
            'message': 'Expense updated'
        })

    return render(request, 'inventory/edit_expense.html', {
        'expense': expense,
        'categories': categories
    })


def delete_expense(request, expense_id):
    try:
        expense = Expense.objects.get(id=expense_id)
    except Expense.DoesNotExist:
        return HttpResponse("Expense not found")

    expense.delete()

    return render(request, 'inventory/expense_list.html', {
        'expenses': Expense.objects.all(),
        'message': 'Expense deleted'
    })