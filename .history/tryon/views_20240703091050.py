import os
import replicate
import logging
from django.conf import settings
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import TryOnResult
from .serializers import TryOnResultSerializer
from shop.models import Product

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def try_on(request):
    logger.info("Received try-on request")
    product_id = request.data.get('product_id')
    logger.info(f"Product ID: {product_id}")
    
    if not product_id:
        logger.warning("Product ID not provided")
        return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        product = Product.objects.get(id=product_id)
        logger.info(f"Found product: {product}")
    except Product.DoesNotExist:
        logger.warning(f"Product with ID {product_id} not found")
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
    
    # Nastavte API token pro Replicate
    os.environ["REPLICATE_API_TOKEN"] = "r8_dgVuU2aOUvNUTxWDNf1RH5vqjREXCqb2tPRHW"
    
    # Připravte vstupní data pro model
    base_url = request.build_absolute_uri('/').rstrip('/')
    human_img_url = request.user.profile_image.url if request.user.profile_image else None
    if human_img_url and not human_img_url.startswith(('http://', 'https://')):
        human_img_url = f"{base_url}{human_img_url}"

    input_data = {
        "garm_img": product.image_url,
        "human_img": human_img_url,
        "garment_des": f"{product.manufacturer_name} {product.name}"
    }
    logger.info(f"Input data: {input_data}")
    
    if not human_img_url:
        logger.warning("User doesn't have a profile image")
        return Response({"error": "User doesn't have a profile image."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate URLs
    validate_url = URLValidator()
    try:
        validate_url(input_data["garm_img"])
        validate_url(input_data["human_img"])
    except ValidationError as e:
        logger.warning(f"Invalid URL: {str(e)}")
        return Response({"error": f"Invalid URL: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Spusťte model
        logger.info("Running Replicate model")
        output = replicate.run(
            "cuuupid/idm-vton:906425dbca90663ff5427624839572cc56ea7d380343d13e2a4c4b09d3f0c30f",
            input=input_data
        )
        logger.info(f"Replicate output: {output}")
        
        # Uložte výsledek do databáze
        try_on_result = TryOnResult.objects.create(
            user=request.user,
            product=product,
            result_image=output
        )
        
        serializer = TryOnResultSerializer(try_on_result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except replicate.exceptions.ReplicateError as e:
        logger.error(f"Replicate API error: {str(e)}", exc_info=True)
        return Response({"error": f"Replicate API error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_try_on_results(request):
    logger.info(f"Fetching try-on results for user: {request.user.username}")
    try_on_results = TryOnResult.objects.filter(user=request.user)
    serializer = TryOnResultSerializer(try_on_results, many=True)
    return Response(serializer.data)