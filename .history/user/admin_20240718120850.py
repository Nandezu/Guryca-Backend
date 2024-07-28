from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, FavoriteItem
from django.utils import timezone

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'gender', 'shopping_region', 'subscription_type', 'subscription_status', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'gender', 'shopping_region', 'subscription_type')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('subscription_start_date', 'subscription_end_date', 'virtual_try_ons_remaining', 'profile_images_remaining', 'try_on_results_remaining')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'gender', 'shopping_region')}),
        (_('Profile Images'), {'fields': ('profile_images',)}),
        (_('Subscription'), {'fields': ('subscription_type', 'subscription_start_date', 'subscription_end_date',
                                        'virtual_try_ons_remaining', 'profile_images_remaining', 'try_on_results_remaining')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'gender', 'shopping_region', 'subscription_type'),
        }),
    )

    def subscription_status(self, obj):
        if obj.subscription_type == 'free':
            return 'Free'
        if obj.subscription_end_date and obj.subscription_end_date > timezone.now():
            return 'Active'
        return 'Inactive'
    subscription_status.short_description = 'Subscription Status'

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = self.model.objects.get(pk=obj.pk)
            if old_obj.subscription_type != obj.subscription_type:
                obj.update_subscription(obj.subscription_type)
        super().save_model(request, obj, form, change)

@admin.register(FavoriteItem)
class FavoriteItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__name')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'product')