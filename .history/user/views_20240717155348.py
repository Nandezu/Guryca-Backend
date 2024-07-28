import os
import logging
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings
import mimetypes
import uuid
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import authenticate
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .models import CustomUser, FavoriteItem
from .serializers import CustomUserSerializer, FavoriteItemSerializer, FavoriteItemCreateSerializer

logger = logging.getLogger(__name__)

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_serializer(self, *args, **kwargs):
        if self.action == 'create':
            kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)

    @action(detail=True, methods=['POST'])
    def upload_profile_image(self, request, pk=None):
        logger.info(f"Received upload_profile_image request for user {pk}")
        user = self.get_object()
        if 'profile_image' not in request.FILES:
            logger.warning("No image provided in request")
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
            
            if 'from_image_detail' in request.query_params:
                s3_url += '?from_image_detail=true'

            user.profile_images.append(s3_url)
            user.save()

            logger.info(f"Profile image uploaded successfully for user {pk}")
            return Response({'message': 'Profile image uploaded successfully', 'image_url': s3_url})
        except Exception as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['POST'])
    def add_profile_image(self, request, pk=None):
        logger.info(f"Received add_profile_image request for user {pk}")
        request.query_params._mutable = True
        request.query_params['from_image_detail'] = 'true'
        return self.upload_profile_image(request, pk)

    @action(detail=True, methods=['DELETE'])
    def remove_profile_image(self, request, pk=None):
        logger.info(f"Received remove_profile_image request for user {pk}")
        user = self.get_object()
        image_url = request.data.get('image_url')
        
        if image_url in user.profile_images:
            user.profile_images.remove(image_url)
            user.save()
            logger.info(f"Profile image removed successfully for user {pk}")
            return Response({'message': 'Profile image removed successfully'})
        else:
            logger.warning(f"Image not found for user {pk}: {image_url}")
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'])
    def set_active_profile_image(self, request, pk=None):
        logger.info(f"Received set_active_profile_image request for user {pk}")
        user = self.get_object()
        image_url = request.data.get('image_url')
        
        if not image_url:
            logger.warning(f"No image_url provided for user {pk}")
            return Response({'error': 'image_url is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if image_url in user.profile_images:
            user.profile_images.remove(image_url)
            user.profile_images.insert(0, image_url)
            user.save()
            logger.info(f"Active profile image set successfully for user {pk}")
            return Response({'message': 'Active profile image set successfully'})
        else:
            logger.warning(f"Image not found for user {pk}: {image_url}")
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_username(request):
    user = request.user
    new_username = request.data.get('newUserName')
    password = request.data.get('password')

    if not new_username or not password:
        return Response({'error': 'Both new username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(password):
        return Response({'error': 'Incorrect password.'}, status=status.HTTP_401_UNAUTHORIZED)

    user.username = new_username
    user.save()
    return Response({'message': 'Username changed successfully.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_email(request):
    user = request.user
    new_email = request.data.get('newEmail')
    password = request.data.get('password')

    if not new_email or not password:
        return Response({'error': 'Both new email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(password):
        return Response({'error': 'Incorrect password.'}, status=status.HTTP_401_UNAUTHORIZED)

    if CustomUser.objects.filter(email=new_email).exists():
        return Response({'error': 'Email is already registered.'}, status=status.HTTP_400_BAD_REQUEST)

    user.email = new_email
    user.save()
    return Response({'message': 'Email changed successfully.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    current_password = request.data.get('currentPassword')
    new_password = request.data.get('newPassword')
    confirm_new_password = request.data.get('confirmNewPassword')

    logger.info(f"Password change request for user {user.id}: current_password={current_password}, new_password={new_password}, confirm_new_password={confirm_new_password}")

    if not current_password or not new_password or not confirm_new_password:
        logger.warning("Password change failed: All password fields are required.")
        return Response({'error': 'All password fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if new_password != confirm_new_password:
        logger.warning("Password change failed: New passwords do not match.")
        return Response({'error': 'New passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(current_password):
        logger.warning("Password change failed: Incorrect current password.")
        return Response({'error': 'Incorrect current password.'}, status=status.HTTP_401_UNAUTHORIZED)

    user.set_password(new_password)
    user.save()
    logger.info(f"Password changed successfully for user {user.id}.")
    return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_region(request):
    user = request.user
    new_region = request.data.get('newRegion')

    if not new_region:
        return Response({'error': 'New region is required.'}, status=status.HTTP_400_BAD_REQUEST)

    user.shopping_region = new_region
    user.save()
    return Response({'message': 'Region changed successfully.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def purchase_subscription(request):
    user = request.user
    plan_type = request.data.get('plan_type')
    duration = request.data.get('duration', 30)  # Výchozí hodnota je 30 dní

    if plan_type not in ['basic', 'pro', 'premium']:
        return Response({'error': 'Invalid plan type'}, status=status.HTTP_400_BAD_REQUEST)

    # Zde by byla logika pro zpracování platby

    user.subscription_type = plan_type
    user.subscription_start_date = timezone.now()
    user.subscription_end_date = user.subscription_start_date + relativedelta(days=duration)
    user.reset_monthly_limits()
    user.save()

    return Response({'message': f'{plan_type.capitalize()} plan purchased successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription_details(request):
    user = request.user
    return Response({
        'subscription_type': user.subscription_type,
        'is_active': user.is_subscription_active,
        'end_date': user.subscription_end_date,
        'virtual_try_ons_remaining': user.virtual_try_ons_remaining,
        'profile_images_remaining': user.profile_images_remaining,
        'try_on_results_remaining': user.try_on_results_remaining
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def use_try_on(request):
    user = request.user
    success, message = user.use_feature('virtual_try_on')
    if success:
        return Response({
            'message': message,
            'virtual_try_ons_remaining': user.virtual_try_ons_remaining
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def use_feature(request):
    user = request.user
    feature_type = request.data.get('feature_type')

    if not user.is_subscription_active:
        return Response({'error': 'Your subscription is not active'}, status=status.HTTP_403_FORBIDDEN)
    success, message = user.use_feature(feature_type)
    if success:
        return Response({
            'message': message,
            'virtual_try_ons_remaining': user.virtual_try_ons_remaining,
            'profile_images_remaining': user.profile_images_remaining,
            'try_on_results_remaining': user.try_on_results_remaining
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    user = request.user
    if user.subscription_type == 'free':
        return Response({'error': 'You do not have an active paid subscription'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Zde by byla logika pro zrušení předplatného v platebním systému

    user.subscription_type = 'free'
    user.subscription_end_date = timezone.now()
    user.reset_monthly_limits()
    user.save()

    return Response({'message': 'Subscription cancelled successfully'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_subscription(request):
    user = request.user
    new_plan_type = request.data.get('new_plan_type')

    if new_plan_type not in ['basic', 'pro', 'premium']:
        return Response({'error': 'Invalid plan type'}, status=status.HTTP_400_BAD_REQUEST)

    if user.subscription_type == new_plan_type:
        return Response({'error': 'You are already subscribed to this plan'}, status=status.HTTP_400_BAD_REQUEST)

    # Zde by byla logika pro změnu předplatného v platebním systému

    user.subscription_type = new_plan_type
    user.reset_monthly_limits()
    user.save()

    return Response({'message': f'Subscription changed to {new_plan_type} successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_plans(request):
    plans = [
        {
            'name': 'Free Plan',
            'price': '$0',
            'features': ['5 VIRTUAL TRY-ONS', '3 PROFILE IMAGES', '7 TRY-ON RESULTS'],
            'ai_section': False,
            'new_section': False
        },
        {
            'name': 'Basic Plan',
            'price': '$7',
            'features': ['50 VIRTUAL TRY-ONS', '5 PROFILE IMAGES', '20 TRY-ON RESULTS'],
            'ai_section': True,
            'new_section': True
        },
        {
            'name': 'Pro Plan',
            'price': '$12',
            'features': ['100 VIRTUAL TRY-ONS', '8 PROFILE IMAGES', '40 TRY-ON RESULTS'],
            'ai_section': True,
            'new_section': True
        },
        {
            'name': 'Premium Plan',
            'price': '$20',
            'features': ['300 VIRTUAL TRY-ONS', '20 PROFILE IMAGES', '60 TRY-ON RESULTS'],
            'ai_section': True,
            'new_section': True
        }
    ]
    return Response(plans)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manual_subscription_update(request):
    if not request.user.is_staff:
        return Response({'error': 'You do not have permission to perform this action'}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get('user_id')
    new_plan_type = request.data.get('new_plan_type')
    duration = request.data.get('duration', 30)  # Výchozí hodnota je 30 dní

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if new_plan_type not in ['free', 'basic', 'pro', 'premium']:
        return Response({'error': 'Invalid plan type'}, status=status.HTTP_400_BAD_REQUEST)

    user.subscription_type = new_plan_type
    user.subscription_start_date = timezone.now()
    user.subscription_end_date = user.subscription_start_date + relativedelta(days=duration)
    user.reset_monthly_limits()
    user.save()

    return Response({'message': f'Subscription manually updated to {new_plan_type} for user {user.username}'}, status=status.HTTP_200_OK)