import os
import replicate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import TryOnResult
from .serializers import TryOnResultSerializer
from shop.models import Product

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def try_on(request):
    product_id = request.data.get('product_id')
    if not product_id:
        return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    # Nastavte API token pro Replicate
    os.environ["REPLICATE_API_TOKEN"] = "váš_replicate_api_token"

    # Připravte vstupní data pro model
    input_data = {
        "garm_img": product.image_url,
        "human_img": request.user.profile_image.url if request.user.profile_image else None,
        "garment_des": f"{product.manufacturer_name} {product.name}"
    }

    try:
        # Spusťte model
        output = replicate.run(
            "cuuupid/idm-vton:906425dbca90663ff5427624839572cc56ea7d380343d13e2a4c4b09d3f0c30f",
            input=input_data
        )

        # Uložte výsledek
        try_on_result = TryOnResult.objects.create(
            user=request.user,
            product=product,
            result_image=output
        )

        serializer = TryOnResultSerializer(try_on_result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)