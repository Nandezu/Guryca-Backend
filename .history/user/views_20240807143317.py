import os
import logging
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings
import mimetypes
import uuid
import secrets
import random
import json
import time
import requests
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import authenticate
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser, FavoriteItem, TemporaryRegistration
from .serializers import CustomUserSerializer, FavoriteItemSerializer, FavoriteItemCreateSerializer, SubscriptionPlanSerializer

logger = logging.getLogger(__name__)

# Apple App Store konstanty
APPLE_BUNDLE_ID = 'com.nandezu.nandefrond'
APPLE_SHARED_SECRET = '588ae1e916b24e2a957e2ed3faa5714c'

# Google Play konstanty (pro budoucí implementaci)
GOOGLE_PACKAGE_NAME = 'com.nandezu.nandefrond'

# Mapování produktů na typy předplatného a dobu trvání
SUBSCRIPTION_MAPPING = {
    'com.nandezu.basic_monthly': ('basic', 30),
    'com.nandezu.promonthly': ('pro', 30),
    'com.nandezu.premiummonthly': ('premium', 30),
    'com.nandezu.basicannual': ('basic', 365),
    'com.nandezu.proannual': ('pro', 365),
    'com.nandezu.premiumannual': ('premium', 365),
}

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [IsAuthenticated]

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
            elif 'is_new_upload' in request.query_params:
                s3_url += '?is_new_upload=true'

            if len(user.profile_images) >= user.profile_images_remaining:
                return Response({'error': 'Profile image limit reached. Please delete an existing image before adding a new one.'}, status=status.HTTP_400_BAD_REQUEST)
            
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

    @action(detail=True, methods=['GET'])
    def get_tryon_results(self, request, pk=None):
        logger.info(f"Received get_tryon_results request for user {pk}")
        user = self.get_object()
        
        tryon_results = user.tryon_results.all()
        
        if tryon_results.count() > 100:
            excess_results = tryon_results.count() - 100
            for tryon_result in tryon_results.order_by('created_at')[:excess_results]:
                tryon_result.delete()

        return Response({'tryon_results': [result.image_url for result in tryon_results]})

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
def pre_register(request):
    logger.info(f"Received pre-register request data: {request.data}")
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        confirmation_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        temp_reg = TemporaryRegistration(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            shopping_region=serializer.validated_data.get('shopping_region', ''),
            gender=serializer.validated_data.get('gender', ''),
            confirmation_code=confirmation_code
        )
        temp_reg.save()
        
        subject = 'Confirm your email for Nandezu'
        html_message = render_to_string('emails/email_confirmation.html', {
            'confirmation_code': confirmation_code
        })
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = serializer.validated_data['email']

        send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
        
        response_data = {
            'message': 'Please check your email for the confirmation code.',
            'email': serializer.validated_data['email']
        }
        logger.info(f"Pre-registration successful for email: {serializer.validated_data['email']}")
        return Response(response_data, status=status.HTTP_201_CREATED)
    logger.warning(f"Pre-registration failed: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def confirm_email(request):
    email = request.data.get('email')
    confirmation_code = request.data.get('confirmation_code')
    
    try:
        temp_reg = TemporaryRegistration.objects.get(email=email, confirmation_code=confirmation_code)
    except TemporaryRegistration.DoesNotExist:
        return Response({'error': 'Invalid email or confirmation code'}, status=status.HTTP_400_BAD_REQUEST)

    if temp_reg.expires_at < timezone.now():
        temp_reg.delete()
        return Response({'error': 'Confirmation code has expired'}, status=status.HTTP_400_BAD_REQUEST)

    user = CustomUser.objects.create_user(
        username=temp_reg.username,
        email=temp_reg.email,
        password=temp_reg.password,
        shopping_region=temp_reg.shopping_region,
        gender=temp_reg.gender
    )
    user.email_confirmed = True
    user.save()

    temp_reg.delete()

    token, _ = Token.objects.get_or_create(user=user)
    response_data = {
        'token': token.key,
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'message': 'Email confirmed and registration completed successfully.'
    }
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def resend_confirmation(request):
    email = request.data.get('email')
    
    try:
        temp_reg = TemporaryRegistration.objects.get(email=email)
    except TemporaryRegistration.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    temp_reg.confirmation_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    temp_reg.save()

    subject = 'Confirm your email for Nandezu'
    html_message = render_to_string('emails/email_confirmation.html', {
        'confirmation_code': temp_reg.confirmation_code
    })
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = temp_reg.email
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

    return Response({'message': 'New confirmation code sent'}, status=status.HTTP_200_OK)

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
    user.email_confirmed = False
    user.generate_confirmation_code()
    user.save()

    subject = 'Confirm your new email for Nandezu'
    html_message = render_to_string('emails/email_confirmation.html', {
        'confirmation_code': user.confirmation_code
    })
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = new_email
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

    return Response({'message': 'Email changed successfully. Please check your new email for the confirmation code.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    current_password = request.data.get('currentPassword')
    new_password = request.data.get('newPassword')
    confirm_new_password = request.data.get('confirmNewPassword')

    logger.info(f"Password change request for user {user.id}")

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

    if plan_type not in ['basic', 'pro', 'premium', 'basic_annual', 'pro_annual', 'premium_annual']:
        return Response({'error': 'Invalid plan type'}, status=status.HTTP_400_BAD_REQUEST)

    # Zde by byla logika pro zpracování platby

    user.update_subscription(plan_type, duration)

    return Response({
        'message': f'{plan_type.replace("_", " ").title()} purchased successfully',
        'subscription_details': CustomUserSerializer(user).data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription_details(request):
    user = request.user
    user.auto_update_free_plan()
    user.auto_update_annual_plans()
    return Response(CustomUserSerializer(user).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def use_feature(request):
    user = request.user
    feature_type = request.data.get('feature_type')

    # Automatické obnovení "Free Plan" limitů
    user.auto_update_free_plan()

    # Automatické obnovení ročních plánů
    user.auto_update_annual_plans()

    success, message = user.use_feature(feature_type)

    if success:
        return Response({
            'success': True,
            'message': message,
            'virtual_try_ons_remaining': user.virtual_try_ons_remaining,
            'subscription_details': CustomUserSerializer(user).data
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    user = request.user
    if user.subscription_type == 'free':
        return Response({'error': 'You do not have an active paid subscription'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Nastavit zrušení předplatného po skončení aktuálního období
    user.is_cancelled = True
    user.save(update_fields=['is_cancelled'])

    return Response({
        'message': 'Subscription cancellation scheduled for end of current period',
        'subscription_details': CustomUserSerializer(user).data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_subscription(request):
    user = request.user
    new_plan_type = request.data.get('new_plan_type')

    if new_plan_type not in ['basic', 'pro', 'premium', 'basic_annual', 'pro_annual', 'premium_annual']:
        return Response({'error': 'Invalid plan type'}, status=status.HTTP_400_BAD_REQUEST)

    if user.subscription_type == new_plan_type:
        return Response({'error': 'You are already subscribed to this plan'}, status=status.HTTP_400_BAD_REQUEST)

    # Zde by byla logika pro změnu předplatného v platebním systému

    user.update_subscription(new_plan_type)

    return Response({
        'message': f'Subscription changed to {new_plan_type.replace("_", " ").title()} successfully',
        'subscription_details': CustomUserSerializer(user).data
    }, status=status.HTTP_200_OK)

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
            'price': '$10',
            'features': ['50 VIRTUAL TRY-ONS', '30 PROFILE IMAGES', '20 TRY-ON RESULTS'],
            'ai_section': True,
            'new_section': True
        },
        {
            'name': 'Pro Plan',
            'price': '$15',
            'features': ['100 VIRTUAL TRY-ONS', '50 PROFILE IMAGES', '40 TRY-ON RESULTS'],
            'ai_section': True,
            'new_section': True
        },
        {
            'name': 'Premium Plan',
            'price': '$25',
            'features': ['200 VIRTUAL TRY-ONS', '100 PROFILE IMAGES', '60 TRY-ON RESULTS'],
            'ai_section': True,
            'new_section': True
        },
        {
            'name': 'Basic Annual Plan',
            'price': '$96',
            'features': ['50 VIRTUAL TRY-ONS monthly', '30 PROFILE IMAGES monthly', '20 TRY-ON RESULTS monthly'],
            'ai_section': True,
            'new_section': True
        },
        {
            'name': 'Pro Annual Plan',
            'price': '$150',
            'features': ['100 VIRTUAL TRY-ONS monthly', '50 PROFILE IMAGES monthly', '40 TRY-ON RESULTS monthly'],
            'ai_section': True,
            'new_section': True
        },
        {
            'name': 'Premium Annual Plan',
            'price': '$250',
            'features': ['200 VIRTUAL TRY-ONS monthly', '100 PROFILE IMAGES monthly', '60 TRY-ON RESULTS monthly'],
            'ai_section': True,
            'new_section': True
        }
    ]
    return Response(SubscriptionPlanSerializer(plans, many=True).data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def manual_subscription_update(request):
    user_id = request.data.get('user_id')
    new_plan_type = request.data.get('new_plan_type')
    duration = request.data.get('duration', 30)  # Výchozí hodnota je 30 dní

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if new_plan_type not in ['free', 'basic', 'pro', 'premium', 'basic_annual', 'pro_annual', 'premium_annual']:
        return Response({'error': 'Invalid plan type'}, status=status.HTTP_400_BAD_REQUEST)

    user.update_subscription(new_plan_type, duration)

    return Response({
        'message': f'Subscription manually updated to {new_plan_type.replace("_", " ").title()} for user {user.username}',
        'subscription_details': CustomUserSerializer(user).data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def reset_password_request(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({'message': 'If an account with this email exists, password reset instructions have been sent.'}, status=status.HTTP_200_OK)

    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_created_at = timezone.now()
    user.save()

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}&email={email}"

    html_message = render_to_string('emails/password_reset_email.html', {'reset_url': reset_url})
    plain_message = strip_tags(html_message)

    subject = 'Reset Your NANDEFROND Password'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    try:
        send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return Response({'error': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'Password reset instructions have been sent to your email'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def reset_password_confirm(request):
    email = request.data.get('email')
    token = request.data.get('token')
    new_password = request.data.get('new_password')

    if not all([email, token, new_password]):
        return Response({'error': 'Email, token and new password are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(email=email, reset_token=token)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Invalid email or token'}, status=status.HTTP_400_BAD_REQUEST)

    # Check token expiration (e.g., 24 hours)
    token_lifetime = timezone.now() - user.reset_token_created_at
    if token_lifetime.total_seconds() > 86400:  # 24 hours in seconds
        return Response({'error': 'Reset token has expired'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.reset_token = None
    user.reset_token_created_at = None
    user.save()

    return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)

def reset_password_page(request):
    token = request.GET.get('token')
    email = request.GET.get('email')
    if token and email:
        return render(request, 'emails/reset_password.html', {'token': token, 'email': email})
    else:
        return Response({'error': 'Invalid token or email'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def verify_purchase(request):
    data = json.loads(request.body)
    platform = data.get('platform')
    
    if platform == 'ios':
        return verify_apple_purchase(request)
    elif platform == 'android':
        return verify_google_purchase(request)
    else:
        return JsonResponse({'error': 'Invalid platform'}, status=400)

@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def verify_apple_purchase(request):
    data = json.loads(request.body)
    receipt_data = data.get('receiptData')

    verify_url = 'https://buy.itunes.apple.com/verifyReceipt'
    # Pro testování použijte: 'https://sandbox.itunes.apple.com/verifyReceipt'

    try:
        response = requests.post(verify_url, json={
            'receipt-data': receipt_data,
            'password': APPLE_SHARED_SECRET,
            'exclude-old-transactions': True
        })

        if response.status_code == 200:
            receipt_info = response.json()
            if receipt_info['status'] == 0:  # 0 znamená platný účet
                latest_receipt_info = receipt_info['latest_receipt_info'][0]
                product_id = latest_receipt_info['product_id']
                expires_date = int(latest_receipt_info['expires_date_ms']) / 1000  # Převod na sekundy
                
                if expires_date > time.time():
                    # Předplatné je stále aktivní
                    update_user_subscription(request.user, product_id, expires_date)
                    return JsonResponse({'success': True, 'message': 'Subscription verified and updated'})
                else:
                    return JsonResponse({'success': False, 'message': 'Subscription has expired'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid receipt'})
        else:
            return JsonResponse({'success': False, 'message': 'Failed to verify with Apple server'})
    except Exception as e:
        logger.error(f"Error verifying Apple purchase: {str(e)}")
        return JsonResponse({'success': False, 'message': 'An error occurred during verification'}, status=500)

@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def verify_google_purchase(request):
    # Toto je zástupné místo pro budoucí implementaci Google Play verifikace
    return JsonResponse({'success': False, 'message': 'Google Play verification not implemented yet'}, status=501)

def update_user_subscription(user, product_id, expires_date):
    try:
        subscription_type, duration = SUBSCRIPTION_MAPPING.get(product_id, (None, None))
        if subscription_type and duration:
            user.subscription_type = subscription_type
            user.subscription_start_date = timezone.now()
            user.subscription_end_date = timezone.fromtimestamp(expires_date)
            user.is_cancelled = False
            user.save()
            
            # Reset limits based on new subscription
            user.reset_monthly_limits()
            
            logger.info(f"Updated subscription for user {user.id} to {subscription_type} until {user.subscription_end_date}")
        else:
            logger.warning(f"Unknown product ID: {product_id}")
    except Exception as e:
        logger.error(f"Error updating user subscription: {str(e)}")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription_details(request):
    user = request.user
    user.auto_update_free_plan()
    user.auto_update_annual_plans()
    return JsonResponse({
        'subscription_type': user.subscription_type,
        'is_active': user.is_subscription_active,
        'end_date': user.subscription_end_date.isoformat() if user.subscription_end_date else None,
        'is_cancelled': user.is_cancelled,
        'virtual_try_ons_remaining': user.virtual_try_ons_remaining,
        'profile_images_remaining': user.profile_images_remaining,
        'try_on_results_remaining': user.try_on_results_remaining
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    user = request.user
    if user.subscription_type == 'free':
        return JsonResponse({'error': 'You do not have an active paid subscription'}, status=400)
    
    user.is_cancelled = True
    user.save()

    return JsonResponse({
        'message': 'Subscription cancellation scheduled for end of current period',
        'end_date': user.subscription_end_date.isoformat()
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def use_feature(request):
    user = request.user
    feature_type = request.data.get('feature_type')

    user.auto_update_free_plan()
    user.auto_update_annual_plans()

    success, message = user.use_feature(feature_type)

    if success:
        return JsonResponse({
            'success': True,
            'message': message,
            'remaining': getattr(user, f"{feature_type}_remaining", 0)
        })
    else:
        return JsonResponse({'error': message}, status=403)

# Další potřebné importy a funkce...

# Zde můžete přidat další views podle potřeby

# Nezapomeňte, že pro plnou funkčnost in-app nákupů budete muset implementovat
# odpovídající logiku na straně klienta (v React Native) pro iniciaci nákupu
# a odeslání potvrzení o nákupu na server k ověření.