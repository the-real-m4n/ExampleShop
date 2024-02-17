from django.shortcuts import render, HttpResponse,redirect
from .models import Product
from .forms import ProductForm

def catalog(request):
    products = Product.objects.all()
    return render(request, 'catalog.html', {'products': products})

def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('catalog')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect('catalog')