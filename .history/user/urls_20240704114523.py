from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, FavoriteItemViewSet, login, LogoutView, register

# Vytvoření routeru pro ViewSety
router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'favorites', FavoriteItemViewSet, basename='favorite')

urlpatterns = [
    # Zahrnutí všech cest generovaných routerem
    path('', include(router.urls)),
    
    # Autentizační cesty
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Cesty pro oblíbené položky
    path('favorites/toggle/', FavoriteItemViewSet.as_view({'post': 'toggle'}), name='favorite-toggle'),
    path('favorites/check/', FavoriteItemViewSet.as_view({'get': 'check'}), name='favorite-check'),
    
    # Cesta pro nahrání profilového obrázku
    path('users/<int:pk>/upload_profile_image/', 
         CustomUserViewSet.as_view({'post': 'upload_profile_image'}), 
         name='user-upload-profile-image'),
]