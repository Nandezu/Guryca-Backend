from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    change_username, change_email, change_password, change_region,
    CustomUserViewSet, FavoriteItemViewSet, login, register, LogoutView,
    reset_password_page, verify_purchase, verify_apple_purchase, verify_google_purchase,
    apple_server_notification, google_server_notification
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'favorites', FavoriteItemViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login, name='login'),
    path('register/', register, name='register'),  # Toto bude nyní dostupné na /user/register/
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change_username/', change_username, name='change-username'),
    path('change_email/', change_email, name='change-email'),
    path('change_password/', change_password, name='change-password'),
    path('change_region/', change_region, name='change-region'),
    path('favorites/toggle/', FavoriteItemViewSet.as_view({'post': 'toggle'}), name='favorite-toggle'),
    path('favorites/check/', FavoriteItemViewSet.as_view({'get': 'check'}), name='favorite-check'),
    path('users/<int:pk>/add_profile_image/',
         CustomUserViewSet.as_view({'post': 'add_profile_image'}),
         name='user-add-profile-image'),
    path('users/<int:pk>/remove_profile_image/',
         CustomUserViewSet.as_view({'delete': 'remove_profile_image'}),
         name='user-remove-profile-image'),
    path('users/<int:pk>/set_active_profile_image/',
         CustomUserViewSet.as_view({'post': 'set_active_profile_image'}),
         name='user-set-active-profile-image'),
    
    # Cesty pro reset hesla
    path('reset-password/', reset_password_page, name='reset-password-page'),
    
    # Cesty pro ověřování nákupů
    path('verify_purchase/', verify_purchase, name='verify-purchase'),
    path('verify_apple_purchase/', verify_apple_purchase, name='verify-apple-purchase'),
    path('verify_google_purchase/', verify_google_purchase, name='verify-google-purchase'),
    
    # Cesty pro server-to-server notifikace
    path('apple-server-notification/', apple_server_notification, name='apple-server-notification'),
    path('google-server-notification/', google_server_notification, name='google-server-notification'),
]