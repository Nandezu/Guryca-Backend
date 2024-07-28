from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from .models import CustomUser, FavoriteItem
from .serializers import CustomUserSerializer, FavoriteItemSerializer, FavoriteItemCreateSerializer

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

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

    token, created = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key, 
        'user_id': user.id, 
        'username': user.username, 
        'email': user.email
    }, status=status.HTTP_200_OK)