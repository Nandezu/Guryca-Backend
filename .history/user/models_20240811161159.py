from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from shop.models import Product
from datetime import timedelta
import random
import string
import secrets

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    shopping_region = models.CharField(max_length=100)
    profile_images = models.JSONField(default=list, blank=True)
    
    subscription_type = models.CharField(max_length=20, choices=[
        ('free', 'Free Plan'),
        ('basic', 'Basic Plan'),
        ('pro', 'Pro Plan'),
        ('premium', 'Premium Plan'),
        ('basic_annual', 'Basic Annual Plan'),
        ('pro_annual', 'Pro Annual Plan'),
        ('premium_annual', 'Premium Annual Plan')
    ], default='free')
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    virtual_try_ons_remaining = models.IntegerField(default=5)
    profile_images_remaining = models.IntegerField(default=3)
    try_on_results_remaining = models.IntegerField(default=7)
    is_cancelled = models.BooleanField(default=False)
    
    reset_token = models.CharField(max_length=100, null=True, blank=True)
    reset_token_created_at = models.DateTimeField(null=True, blank=True)

    google_play_purchase_token = models.CharField(max_length=255, null=True, blank=True)
    google_play_order_id = models.CharField(max_length=255, null=True, blank=True)

    @property
    def active_profile_image(self):
        return self.profile_images[0] if self.profile_images else None

    @property
    def is_subscription_active(self):
        if self.subscription_type == 'free':
            return True
        return self.subscription_end_date > timezone.now() if self.subscription_end_date else False

    def reset_monthly_limits(self):
        limits = {
            'free': (5, 3, 7),
            'basic': (50, 30, 20),
            'pro': (100, 50, 40),
            'premium': (200, 100, 60),
            'basic_annual': (50, 30, 20),
            'pro_annual': (100, 50, 40),
            'premium_annual': (200, 100, 60)
        }
        self.virtual_try_ons_remaining, self.profile_images_remaining, self.try_on_results_remaining = limits.get(self.subscription_type, (5, 3, 7))

    def use_feature(self, feature_type):
        if not self.is_subscription_active and self.subscription_type != 'free':
            return False, "Your subscription is not active"

        feature_map = {
            'virtual_try_on': 'virtual_try_ons_remaining',
            'profile_image': 'profile_images_remaining',
            'try_on_result': 'try_on_results_remaining'
        }

        if feature_type not in feature_map:
            return False, "Invalid feature type"

        remaining_attr = feature_map[feature_type]
        remaining = getattr(self, remaining_attr)

        if remaining > 0:
            setattr(self, remaining_attr, remaining - 1)
            self.save(update_fields=[remaining_attr])
            return True, f"{feature_type.replace('_', ' ').title()} used successfully"
        return False, f"No {feature_type.replace('_', ' ')}s remaining"

    def update_subscription(self, new_type=None, duration=30):
        if new_type:
            self.subscription_type = new_type
        self.subscription_start_date = timezone.now()
        self.subscription_end_date = self.subscription_start_date + timedelta(days=duration)
        self.reset_monthly_limits()
        super().save(update_fields=['subscription_type', 'subscription_start_date', 'subscription_end_date',
                                    'virtual_try_ons_remaining', 'profile_images_remaining', 'try_on_results_remaining'])

    def auto_update_free_plan(self):
        if self.subscription_type == 'free' and (not self.subscription_start_date or not self.subscription_end_date or timezone.now() > self.subscription_end_date):
            self.update_subscription('free')

    def auto_update_annual_plans(self):
        if self.subscription_type in ['basic_annual', 'pro_annual', 'premium_annual']:
            if timezone.now() > self.subscription_end_date:
                self.subscription_start_date = timezone.now()
                self.subscription_end_date = self.subscription_start_date + timedelta(days=365)
            self.reset_monthly_limits()
            super().save(update_fields=['subscription_start_date', 'subscription_end_date', 
                                        'virtual_try_ons_remaining', 'profile_images_remaining', 'try_on_results_remaining'])

    def update_subscription_from_purchase(self, product_id, expires_date):
        subscription_mapping = {
            'com.nandezu.basic_monthly': ('basic', 30),
            'com.nandezu.promonthly': ('pro', 30),
            'com.nandezu.premiummonthly': ('premium', 30),
            'com.nandezu.basicannual': ('basic_annual', 365),
            'com.nandezu.proannual': ('pro_annual', 365),
            'com.nandezu.premiumannual': ('premium_annual', 365),
            'basic.monthly': ('basic', 30),
            'pro.monthly': ('pro', 30),
            'premium.monthly': ('premium', 30),
            'basic.annual': ('basic_annual', 365),
            'pro.annual': ('pro_annual', 365),
            'premium.annual': ('premium_annual', 365),
        }
        
        subscription_type, duration = subscription_mapping.get(product_id, (None, None))
        if subscription_type:
            self.subscription_type = subscription_type
            self.subscription_start_date = timezone.now()
            self.subscription_end_date = timezone.fromtimestamp(expires_date)
            self.is_cancelled = False
            self.reset_monthly_limits()
            self.save()
            return True
        return False

    def check_subscription_validity(self):
        if self.subscription_type != 'free' and self.subscription_end_date:
            if timezone.now() > self.subscription_end_date:
                if not self.is_cancelled:
                    # Zde by mohla být implementována logika pro pokus o obnovu předplatného
                    # Například zavolat API Google Play pro kontrolu stavu předplatného
                    pass
                else:
                    self.subscription_type = 'free'
                    self.save()
                    self.reset_monthly_limits()

    def verify_google_play_purchase(self, purchase_token):
        # Zde by byla implementována logika pro ověření nákupu z Google Play
        # Tato metoda by mohla být volána z views.py před aktualizací předplatného
        pass

    def process_subscription_renewal(self, new_expires_date):
        if self.subscription_type in ['basic', 'pro', 'premium', 'basic_annual', 'pro_annual', 'premium_annual']:
            self.subscription_end_date = timezone.fromtimestamp(new_expires_date)
            self.is_cancelled = False
            self.save(update_fields=['subscription_end_date', 'is_cancelled'])
            return True
        return False

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new or not self.subscription_start_date or not self.subscription_end_date:
            super().save(*args, **kwargs)
            self.update_subscription('free')
        elif self.subscription_type in ['basic_annual', 'pro_annual', 'premium_annual']:
            super().save(*args, **kwargs)
            self.auto_update_annual_plans()
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_created_at = timezone.now()
        self.save(update_fields=['reset_token', 'reset_token_created_at'])

    def is_reset_token_valid(self):
        if not self.reset_token or not self.reset_token_created_at:
            return False
        return (timezone.now() - self.reset_token_created_at) < timedelta(days=3)

    def clear_expired_tokens(self):
        if self.reset_token and not self.is_reset_token_valid():
            self.reset_token = None
            self.reset_token_created_at = None
            self.save(update_fields=['reset_token', 'reset_token_created_at'])

class FavoriteItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.product.name}"