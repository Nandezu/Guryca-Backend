from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import CustomUser, FavoriteItem
from .serializers import CustomUserSerializer, FavoriteItemSerializer, FavoriteItemCreateSerializer
import logging

logger = logging.getLogger(__name__)

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == 'create':
            kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)

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

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        product_id = request.data.get('product')
        favorite = FavoriteItem.objects.filter(user=request.user, product_id=product_id).first()
        
        if favorite:
            favorite.delete()
            return Response({"status": "removed"}, status=status.HTTP_200_OK)
        else:
            serializer = FavoriteItemCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({"status": "added"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'])
    def list_favorites(self, request):
        favorites = self.get_queryset()
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    logger.info(f"Login attempt: username={username}")

    if not username or not password:
        logger.warning("Login failed: Missing username or password")
        return Response({'error': 'Both username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is None:
        logger.warning(f"Authentication failed for username: {username}")
        try:
            user_obj = CustomUser.objects.get(username=username)
            logger.warning(f"User exists but authentication failed. Password correct: {user_obj.check_password(password)}")
        except CustomUser.DoesNotExist:
            logger.warning(f"User with username {username} does not exist")
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

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

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)