from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .models import CustomUser, FavoriteItem, ProfileImage
from .serializers import CustomUserSerializer, FavoriteItemSerializer, FavoriteItemCreateSerializer, ProfileImageSerializer
import logging
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings
import mimetypes
import uuid

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
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        image = request.FILES['profile_image']
        
        # Generování unikátního názvu souboru
        file_extension = image.name.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Nahrání do S3
        try:
            s3 = boto3.client('s3', 
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            s3_file_name = f'profile_images/{unique_filename}'
            
            # Určení Content-Type
            content_type, _ = mimetypes.guess_type(image.name)
            if content_type is None:
                content_type = 'application/octet-stream'

            logger.info(f"Attempting to upload file to S3: {s3_file_name}")
            
            # Nahrání souboru s explicitním Content-Type
            s3.upload_fileobj(
                image,
                bucket_name,
                s3_file_name,
                ExtraArgs={
                    'ContentType': content_type
                }
            )
            
            # Uložení URL obrázku do databáze
            s3_url = f'https://{bucket_name}.s3.amazonaws.com/{s3_file_name}'
            profile_image = ProfileImage(user=user, image=s3_url)
            profile_image.save()

            logger.info(f"File successfully uploaded. URL: {s3_url}")

            return Response({'message': 'Profile image uploaded successfully', 'image_url': s3_url})
        except Exception as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['GET'])
    def profile_images(self, request, pk=None):
        user = self.get_object()
        images = ProfileImage.objects.filter(user=user)
        serializer = ProfileImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path='profile_images/(?P<image_id>\d+)')
    def delete_profile_image(self, request, pk=None, image_id=None):
        user = self.get_object()
        image = get_object_or_404(ProfileImage, id=image_id, user=user)
        image.delete()
        return Response({'message': 'Profile image deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['PUT'])
    def select_profile_image(self, request, pk=None):
        user = self.get_object()
        profile_image_url = request.data.get('profile_image_url')
        user.profile_image_url = profile_image_url
        user.save()
        return Response({'message': 'Profile image selected successfully'}, status=status.HTTP_200_OK)

class FavoriteItemViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavoriteItem.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return FavoriteItemCreateSerializer
        return FavoriteItemSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def check(self, request):
        product_id = request.query_params.get('product')
        user_id = request.query_params.get('user')
       
        if not product_id or not user_id:
            return Response({"error": "Both product and user parameters are required."}, status=status.HTTP_400_BAD_REQUEST)
       
        is_favorite = FavoriteItem.objects.filter(user_id=user_id, product_id=product_id).exists()
        return Response({"is_favorite": is_favorite})

    @action(detail=False, methods=['POST'])
    def toggle(self, request):
        product_id = request.data.get('product')
        favorite, created = FavoriteItem.objects.get_or_create(user=request.user, product_id=product_id)
       
        if not created:
            favorite.delete()
            return Response({"is_favorite": False}, status=status.HTTP_200_OK)
        else:
            return Response({"is_favorite": True}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'])
    def list_favorites(self, request):
        favorites = self.get_queryset()
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)

@api_view(['POST'])
def login(request):
    logger.info(f"Received login request data: {request.data}")
    username = request.data.get('username')
    password = request.data.get('password')

    logger.info(f"Login attempt: username={username}")

    if not username or not password:
        logger.warning("Login failed: Missing username or password")
        return Response({'error': 'Both username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(username=username)
        if user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            user_data = CustomUserSerializer(user).data

            response_data = {
                'token': token.key,
                'user_id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email']
            }

            logger.info(f"Login successful for user: {user.username}")
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Invalid password for user: {username}")
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
    except CustomUser.DoesNotExist:
        logger.warning(f"User not found: {username}")
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def register(request):
    logger.info(f"Received register request data: {request.data}")
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data['password'])
        user.save()
        token, _ = Token.objects.get_or_create(user=user)
        response_data = {
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        }
        logger.info(f"Registration successful for user: {user.username}")
        return Response(response_data, status=status.HTTP_201_CREATED)
    logger.warning(f"Registration failed: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
