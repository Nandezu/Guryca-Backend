from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from .models import Product

class ProductListView(View):
    def get(self, request):
        products = Product.objects.all()
        return render(request, 'shop/product_list.html', {'products': products})

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
        return render(request, 'shop/product_detail.html', {'product': product})

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if 'update' in request.POST:
            product.name = request.POST.get('name', product.name)
            product.description = request.POST.get('description', product.description)
            product.store_link = request.POST.get('store_link', product.store_link)
            product.image_url = request.POST.get('image_url', product.image_url)
            product.sku = request.POST.get('sku', product.sku)
            product.clothing_type = request.POST.get('clothing_type', product.clothing_type)
            product.clothing_category = request.POST.get('clothing_category', product.clothing_category)
            product.manufacturer_name = request.POST.get('manufacturer_name', product.manufacturer_name)
            product.country_of_origin = request.POST.get('country_of_origin', product.country_of_origin)
            product.colour = request.POST.get('colour', product.colour)
            product.price = request.POST.get('price', product.price)
            product.save()
            messages.success(request, f'Product {product.name} has been updated.')
        elif 'delete' in request.POST:
            product.delete()
            messages.success(request, f'Product {product.name} has been deleted.')
            return redirect('product_list')
        return redirect('product_detail', pk=pk)