from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "Nebyly poskytnuty žádné ID k mazání."}, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count = Product.objects.filter(id__in=ids).delete()[0]
        return Response({"message": f"Smazáno {deleted_count} produktů."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put', 'patch'])
    def bulk_update(self, request):
        products_data = request.data.get('products', [])
        if not products_data:
            return Response({"error": "Nebyla poskytnuta žádná data k aktualizaci."}, status=status.HTTP_400_BAD_REQUEST)
        
        updated_count = 0
        for product_data in products_data:
            product_id = product_data.get('id')
            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                    serializer = self.get_serializer(product, data=product_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        updated_count += 1
                except Product.DoesNotExist:
                    pass
        
        return Response({"message": f"Aktualizováno {updated_count} produktů."}, status=status.HTTP_200_OK)