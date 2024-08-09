from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    change_username, change_email, change_password, change_region,
    CustomUserViewSet, FavoriteItemViewSet, login, register, LogoutView,
    reset_password_page, verify_purchase, get_subscription_details,
    cancel_subscription, use_feature, get_available_plans,
    manual_subscription_update
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'favorites', FavoriteItemViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
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
    
    # Cesty pro reset hesla
    path('reset-password/', reset_password_page, name='reset-password-page'),
    
    # Cesty pro správu předplatného
    path('subscription/details/', get_subscription_details, name='subscription-details'),
    path('subscription/cancel/', cancel_subscription, name='cancel-subscription'),
    path('subscription/use_feature/', use_feature, name='use-feature'),
    path('subscription/plans/', get_available_plans, name='available-plans'),
    path('subscription/manual_update/', manual_subscription_update, name='manual-subscription-update'),

    # Cesta pro ověřování nákupů
    path('verify_purchase/', verify_purchase, name='verify-purchase'),
]