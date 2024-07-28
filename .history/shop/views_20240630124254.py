from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=['post'])
    def delete_products(self, request):
        product_ids = request.data.get('ids', [])
        if not product_ids:
            return Response({"error": "Nebyly poskytnuty žádné ID k mazání."}, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count, _ = Product.objects.filter(id__in=product_ids).delete()
        return Response({"message": f"Smazáno {deleted_count} produktů."}, status=status.HTTP_200_OK)