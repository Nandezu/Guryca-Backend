import uuid
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings
import mimetypes

logger = logging.getLogger(__name__)

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == 'create':
            kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)

    @action(detail=True, methods=['POST'])
    def upload_profile_image(self, request, pk=None):
        user = self.get_object()
        if 'profile_image' not in request.FILES:
            logger.error("No image provided")
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        image = request.FILES['profile_image']
        
        # Uložení do SQL databáze
        user.profile_image = image
        user.save()

        # Nahrání do S3
        try:
            s3 = boto3.client('s3', 
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME

            # Generování unikátního názvu souboru
            file_extension = image.name.split('.')[-1]
            unique_filename = f'{uuid.uuid4()}.{file_extension}'
            s3_file_name = f'profile_images/{user.id}/{unique_filename}'
            
            # Určení Content-Type
            content_type, _ = mimetypes.guess_type(image.name)
            if content_type is None:
                content_type = 'application/octet-stream'

            # Nahrání souboru s explicitním Content-Type
            logger.info(f"Uploading file to S3: {s3_file_name}")
            s3.upload_fileobj(
                image,
                bucket_name,
                s3_file_name,
                ExtraArgs={
                    'ContentType': content_type,
                }
            )
            
            # Aktualizace URL obrázku v databázi
            s3_url = f'https://{bucket_name}.s3.amazonaws.com/{s3_file_name}'
            user.profile_image_url = s3_url
            user.save()

            logger.info(f"Profile image updated successfully: {s3_url}")
            return Response({'message': 'Profile image updated successfully', 'image_url': s3_url})
        except NoCredentialsError:
            logger.error("S3 credentials not available")
            return Response({'error': 'S3 credentials not available'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error uploading profile image: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
