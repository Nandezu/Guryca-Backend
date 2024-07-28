import os
import logging
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings
import mimetypes
import uuid
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from .models import CustomUser, FavoriteItem
from .serializers import CustomUserSerializer, FavoriteItemSerializer, FavoriteItemCreateSerializer

logger = logging.getLogger(__name__)

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer(self, *args, **kwargs):
        if self.action == 'create':
            kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)

    @action(detail=True, methods=['POST'])
    def upload_profile_image(self, request, pk=None):
        user = self.get_object()
        if 'profile_image' not in request.FILES:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        image = request.FILES['profile_image']
        
        file_extension = image.name.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        try:
            s3 = boto3.client('s3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            s3_file_name = f'profile_images/{unique_filename}'
            
            content_type, _ = mimetypes.guess_type(image.name)
            if content_type is None:
                content_type = 'application/octet-stream'

            s3.upload_fileobj(
                image,
                bucket_name,
                s3_file_name,
                ExtraArgs={
                    'ContentType': content_type
                }
            )
            
            s3_url = f'https://{bucket_name}.s3.amazonaws.com/{s3_file_name}'
            
            user.profile_images.append(s3_url)
            user.save()

            return Response({'message': 'Profile image uploaded successfully', 'image_url': s3_url})
        except Exception as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['POST'])
    def add_profile_image(self, request, pk=None):
        return self.upload_profile_image(request, pk)

    @action(detail=True, methods=['DELETE'])
    def remove_profile_image(self, request, pk=None):
        user = self.get_object()
        image_url = request.data.get('image_url')
        
        if image_url in user.profile_images:
            user.profile_images.remove(image_url)
            user.save()
            return Response({'message': 'Profile image removed successfully'})
        else:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'])
    def set_active_profile_image(self, request, pk=None):
        user = self.get_object()
        image_url = request.data.get('image_url')
        
        if image_url in user.profile_images:
            user.profile_images.remove(image_url)
            user.profile_images.insert(0, image_url)
            user.save()
            return Response({'message': 'Active profile image set successfully'})
        else:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)

# Zbytek kódu zůstává stejný...