from django.urls import path, include  # Přidán import 'include'
from rest_framework.routers import DefaultRouter  # Přidán import 'DefaultRouter'
from .views import change_username, change_email, change_password, change_region, CustomUserViewSet, FavoriteItemViewSet, login, register, LogoutView

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'favorites', FavoriteItemViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),  # Použití 'include' pro router
    path('login/', login, name='login'),
    path('register/', register, name='register'),
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
]
