import os
import replicate
import logging
import requests
import time
from django.conf import settings
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import TryOnResult
from .serializers import TryOnResultSerializer
from shop.models import Product

logger = logging.getLogger(__name__)

def is_url_accessible(url, timeout=20):
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException as e:
        logger.warning(f"URL accessibility check failed for {url}: {e}")
        return False

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
   
    os.environ["REPLICATE_API_TOKEN"] = "r8_dgVuU2aOUvNUTxWDNf1RH5vqjREXCqb2tPRHW"
   
    user_profile_image_url = request.user.profile_image_url
    if not user_profile_image_url:
        logger.warning(f"User {request.user.username} does not have a profile image")
        return Response({"error": "User does not have a profile image."}, status=status.HTTP_400_BAD_REQUEST)
   
    input_data = {
        "garm_img": product.image_url,
        "human_img": user_profile_image_url,
        "garment_des": product.clothing_type,
        "category": product.clothing_type
    }
    logger.info(f"Input data: {input_data}")
   
    validate_url = URLValidator()
    try:
        validate_url(input_data["garm_img"])
        validate_url(input_data["human_img"])
        if not is_url_accessible(input_data["garm_img"]) or not is_url_accessible(input_data["human_img"]):
            raise ValidationError("URL is not accessible")
    except ValidationError as e:
        logger.warning(f"Invalid or inaccessible URL: {str(e)}")
        return Response({"error": f"Invalid or inaccessible URL: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
   
    try:
        logger.info("Running Replicate model")
        output = replicate.run(
            "cuuupid/idm-vton:906425dbca90663ff5427624839572cc56ea7d380343d13e2a4c4b09d3f0c30f",
            input=input_data
        )
        logger.info(f"Replicate output: {output}")
        
        response = requests.get(output)
        if response.status_code == 200:
            file_name = f"tryon_{request.user.id}_{product.id}_{int(time.time())}.jpg"
            
            file_content = ContentFile(response.content)
            file_path = default_storage.save(f'tryon_results/{file_name}', file_content)
            
            file_url = default_storage.url(file_path)
            
            try_on_result = TryOnResult.objects.create(
                user=request.user,
                product=product,
                result_image=file_url
            )
            
            serializer = TryOnResultSerializer(try_on_result)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Failed to download image from API"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
    try_on_results = TryOnResult.objects.filter(user=request.user).order_by('-created_at')[:20]  # Omezení na posledních 20 výsledků
    serializer = TryOnResultSerializer(try_on_results, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_try_on_result(request, result_id):
    logger.info(f"Attempting to delete try-on result with ID: {result_id} for user: {request.user.username}")
    try:
        result = TryOnResult.objects.get(id=result_id, user=request.user)
        logger.info(f"Found try-on result: {result}")
        
        # Odstranění souboru z S3
        if result.result_image:
            try:
                logger.info(f"Attempting to delete file: {result.result_image.name}")
                default_storage.delete(result.result_image.name)
                logger.info("File deleted successfully")
            except Exception as e:
                logger.error(f"Error deleting file from storage: {str(e)}", exc_info=True)
                # Pokračujeme v mazání záznamu z databáze, i když se nepodařilo smazat soubor
        
        result.delete()
        logger.info("Try-on result deleted successfully")
        return Response(status=status.HTTP_204_NO_CONTENT)
    except TryOnResult.DoesNotExist:
        logger.warning(f"Try-on result with ID {result_id} not found for user {request.user.username}")
        return Response({"error": "Try-on result not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error deleting try-on result: {str(e)}", exc_info=True)
        return Response({"error": "An unexpected error occurred while deleting the try-on result"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)