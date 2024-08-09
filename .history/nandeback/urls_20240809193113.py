from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from shop.views import ProductViewSet
from user.views import (
    CustomUserViewSet, FavoriteItemViewSet,
    get_subscription_details, use_feature,
    cancel_subscription, get_available_plans,
    manual_subscription_update, reset_password_request, reset_password_confirm,
    verify_purchase
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
    path('user/', include('user.urls')),  # Toto zahrne všechny cesty z user/urls.py
    path('tryon/', include('tryon.urls')),
    
    # Cesty pro funkce související s předplatným
    path('subscription/details/', get_subscription_details, name='subscription-details'),
    path('subscription/use_feature/', use_feature, name='use-feature'),
    path('subscription/cancel/', cancel_subscription, name='cancel-subscription'),
    path('subscription/plans/', get_available_plans, name='available-plans'),
    path('subscription/manual_update/', manual_subscription_update, name='manual-subscription-update'),
    
    # Cesta pro ověření nákupu
    path('verify_purchase/', verify_purchase, name='verify-purchase'),
    
    # Cesty pro reset hesla
    path('user/reset-password-request/', reset_password_request, name='reset-password-request'),
    path('user/reset-password-confirm/', reset_password_confirm, name='reset-password-confirm'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)