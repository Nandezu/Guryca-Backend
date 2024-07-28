from django.contrib import admin
from .models import CustomUser, FavoriteItem

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'gender', 'shopping_region')
    search_fields = ('username', 'email')

@admin.register(FavoriteItem)
class FavoriteItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('user', 'product')
    search_fields = ('user__username', 'product__name')