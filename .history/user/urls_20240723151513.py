from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    change_username, change_email, change_password, change_region,
    CustomUserViewSet, FavoriteItemViewSet, login, register, LogoutView,
    purchase_subscription, get_subscription_details, use_feature,
    cancel_subscription, change_subscription, get_available_plans,
    manual_subscription_update, confirm_email, resend_confirmation
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
    
    # Cesty pro funkce související s předplatným
    path('subscription/purchase/', purchase_subscription, name='purchase-subscription'),
    path('subscription/details/', get_subscription_details, name='subscription-details'),
    path('subscription/use_feature/', use_feature, name='use-feature'),
    path('subscription/cancel/', cancel_subscription, name='cancel-subscription'),
    path('subscription/change/', change_subscription, name='change-subscription'),
    path('subscription/plans/', get_available_plans, name='available-plans'),
    path('subscription/manual_update/', manual_subscription_update, name='manual-subscription-update'),

    # Nové cesty pro potvrzení e-mailu
    path('confirm_email/', confirm_email, name='confirm-email'),
    path('resend_confirmation/', resend_confirmation, name='resend-confirmation'),
]