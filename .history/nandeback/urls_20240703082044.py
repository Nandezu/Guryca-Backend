from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from shop.views import ProductViewSet  # Předpokládám, že ProductViewSet je v aplikaci 'shop'
from user.views import login, register, CustomUserViewSet, FavoriteItemViewSet, LogoutView
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
    path('user/register/', register, name='register'),
    path('user/logout/', LogoutView.as_view(), name='logout'),
    path('favorites/toggle/', FavoriteItemViewSet.as_view({'post': 'toggle'}), name='favorite-toggle'),
    path('user/', include('user.urls')),
    path('tryon/', include('tryon.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)