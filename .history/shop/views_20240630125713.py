from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Product
from django.contrib import messages

class ProductListView(View):
    def get(self, request):
        products = Product.objects.all()
        return render(request, 'shop/product_list.html', {'products': products})  # Upraveno zde

    def post(self, request):
        if 'delete' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product.delete()
            messages.success(request, f'Product {product.name} has been deleted.')
        return redirect('product_list')

class ProductDetailView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return render(request, 'shop/product_detail.html', {'product': product})  # Upraveno zde

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if 'update' in request.POST:
            product.name = request.POST.get('name', product.name)
            product.description = request.POST.get('description', product.description)
            # Přidejte další pole podle potřeby
            product.save()
            messages.success(request, f'Product {product.name} has been updated.')
        elif 'delete' in request.POST:
            product.delete()
            messages.success(request, f'Product {product.name} has been deleted.')
            return redirect('product_list')
        return redirect('product_detail', pk=pk)