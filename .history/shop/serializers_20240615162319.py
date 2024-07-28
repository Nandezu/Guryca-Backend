from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'store_link', 'image_url', 'sku', 'clothing_type', 'clothing_category', 'manufacturer_name', 'country_of_origin']
