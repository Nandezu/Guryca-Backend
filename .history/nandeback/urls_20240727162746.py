from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from shop.views import ProductViewSet
from user.views import (
    login, pre_register, CustomUserViewSet, FavoriteItemViewSet, LogoutView,
    purchase_subscription, get_subscription_details, use_feature,
    cancel_subscription, change_subscription, get_available_plans,
    manual_subscription_update, confirm_email, resend_confirmation,
    reset_password_request, reset_password_confirm, reset_password_page
)
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'users', CustomUserViewSet)
router.register(r'favorites', FavoriteItemViewSet, basename='favorite')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    
    # User related paths
    path('user/', include([
        path('login/', login, name='login'),
        path('pre-register/', pre_register, name='pre-register'),
        path('logout/', LogoutView.as_view(), name='logout'),
        path('confirm-email/', confirm_email, name='confirm-email'),
        path('resend-confirmation/', resend_confirmation, name='resend-confirmation'),
        path('reset-password-request/', reset_password_request, name='reset-password-request'),
        path('reset-password-confirm/', reset_password_confirm, name='reset-password-confirm'),
    ])),
    
    path('reset-password/<str:token>/', reset_password_page, name='reset-password-page'),
    
    path('favorites/toggle/', FavoriteItemViewSet.as_view({'post': 'toggle'}), name='favorite-toggle'),
    
    # Subscription related paths
    path('subscription/', include([
        path('purchase/', purchase_subscription, name='purchase-subscription'),
        path('details/', get_subscription_details, name='subscription-details'),
        path('use_feature/', use_feature, name='use-feature'),
        path('cancel/', cancel_subscription, name='cancel-subscription'),
        path('change/', change_subscription, name='change-subscription'),
        path('plans/', get_available_plans, name='available-plans'),
        path('manual_update/', manual_subscription_update, name='manual-subscription-update'),
    ])),
    
    path('tryon/', include('tryon.urls')),
    
    # Favicon path
    path('favicon.ico', lambda request: HttpResponse(status=204)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)