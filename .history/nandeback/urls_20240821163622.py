from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from shop.views import ProductViewSet
from user.views import (
    CustomUserViewSet, FavoriteItemViewSet,
    get_subscription_details, use_feature,
    cancel_subscription, get_available_plans,
    manual_subscription_update, reset_password_request, reset_password_confirm,
    purchase_subscription, change_subscription, 
    purchase_webhook, apple_server_to_server_notification, google_real_time_notification
)
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'users', CustomUserViewSet)
router.register(r'favorites', FavoriteItemViewSet, basename='favorite')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('user/', include('user.urls')),
    path('tryon/', include('tryon.urls')),
    
    # Subscription related paths
    path('subscription/', include([
        path('details/', get_subscription_details, name='subscription-details'),
        path('use_feature/', use_feature, name='use-feature'),
        path('cancel/', cancel_subscription, name='cancel-subscription'),
        path('plans/', get_available_plans, name='available-plans'),
        path('manual_update/', manual_subscription_update, name='manual-subscription-update'),
        path('purchase/', purchase_subscription, name='purchase-subscription'),
        path('change/', change_subscription, name='change-subscription'),
    ])),
    
    # Password reset
    path('user/reset-password-request/', reset_password_request, name='reset-password-request'),
    path('user/reset-password-confirm/', reset_password_confirm, name='reset-password-confirm'),
    
    # Purchase webhooks
    path('purchase-webhook/', purchase_webhook, name='purchase-webhook'),
    path('apple-webhook/', apple_server_to_server_notification, name='apple-webhook'),
    path('google-webhook/', google_real_time_notification, name='google-webhook'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)