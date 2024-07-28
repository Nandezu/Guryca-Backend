from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from shop.views import ProductViewSet
from user.views import (
    login, pre_register, CustomUserViewSet, FavoriteItemViewSet, LogoutView,
    purchase_subscription, get_subscription_details, use_feature,
    cancel_subscription, change_subscription, get_available_plans,
    manual_subscription_update, confirm_email, resend_confirmation,
    reset_password_request, reset_password_confirm
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
    path('user/login/', login, name='login'),
    path('user/pre-register/', pre_register, name='pre-register'),
    path('user/logout/', LogoutView.as_view(), name='logout'),
    path('favorites/toggle/', FavoriteItemViewSet.as_view({'post': 'toggle'}), name='favorite-toggle'),
    path('user/', include('user.urls')),
    path('tryon/', include('tryon.urls')),
    
    # Cesty pro funkce související s předplatným
    path('subscription/purchase/', purchase_subscription, name='purchase-subscription'),
    path('subscription/details/', get_subscription_details, name='subscription-details'),
    path('subscription/use_feature/', use_feature, name='use-feature'),
    path('subscription/cancel/', cancel_subscription, name='cancel-subscription'),
    path('subscription/change/', change_subscription, name='change-subscription'),
    path('subscription/plans/', get_available_plans, name='available-plans'),
    path('subscription/manual_update/', manual_subscription_update, name='manual-subscription-update'),
    
    # Cesty pro potvrzení e-mailu
    path('user/confirm-email/', confirm_email, name='confirm-email'),
    path('user/resend-confirmation/', resend_confirmation, name='resend-confirmation'),
    
    # Cesty pro reset hesla
    path('user/reset-password-request/', reset_password_request, name='reset-password-request'),
    path('user/reset-password-confirm/', reset_password_confirm, name='reset-password-confirm'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)