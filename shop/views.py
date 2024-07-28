from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['clothing_category']

    def list(self, request, *args, **kwargs):
        # Pro účely ladění vypíšeme požadavek a parametry
        print("Request params:", request.query_params)
        return super().list(request, *args, **kwargs)