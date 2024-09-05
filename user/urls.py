from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    purchase_webhook,
    change_username, change_email, change_password, change_region,
    CustomUserViewSet, FavoriteItemViewSet, login, register, LogoutView,
    reset_password_page, reset_password_request, reset_password_confirm,
    get_subscription_details, purchase_subscription, cancel_subscription,
    use_feature, get_available_plans, change_subscription,
    manual_subscription_update,
    apple_server_to_server_notification,
    google_real_time_notification,
    redirect_to_payment,  # Nový import
    stripe_webhook,  # Nový import
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
    path('reset-password-request/', reset_password_request, name='reset-password-request'),
    path('reset-password-confirm/', reset_password_confirm, name='reset-password-confirm'),
    
    # Cesty pro správu předplatného
    path('subscription/details/', get_subscription_details, name='subscription-details'),
    path('subscription/purchase/', purchase_subscription, name='purchase-subscription'),
    path('subscription/cancel/', cancel_subscription, name='cancel-subscription'),
    path('subscription/change/', change_subscription, name='change-subscription'),
    path('subscription/use_feature/', use_feature, name='use-feature'),
    path('subscription/plans/', get_available_plans, name='available-plans'),
    path('subscription/manual_update/', manual_subscription_update, name='manual-subscription-update'),
    
    # Webhooky pro nákupy
    path('purchase-webhook/', purchase_webhook, name='purchase-webhook'),
    path('apple-webhook/', apple_server_to_server_notification, name='apple-webhook'),
    path('google-webhook/', google_real_time_notification, name='google-webhook'),

    # Nové cesty pro Stripe Payment Links
    path('buy-credits/', redirect_to_payment, name='buy-credits'),
    path('stripe-webhook/', stripe_webhook, name='stripe-webhook'),
]