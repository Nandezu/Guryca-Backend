from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, FavoriteItemViewSet, login, LogoutView, register

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'favorites', FavoriteItemViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login, name='login'),  # Explicitní cesta pro login
    path('register/', register, name='register'),  # Přidána cesta pro registraci
    path('logout/', LogoutView.as_view(), name='logout'),
    path('favorites/toggle/', FavoriteItemViewSet.as_view({'post': 'toggle'}), name='favorite-toggle'),
]
