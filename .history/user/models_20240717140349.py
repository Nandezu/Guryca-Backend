from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from shop.models import Product
from django.db.models.signals import pre_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    shopping_region = models.CharField(max_length=100)
    profile_images = models.JSONField(default=list, blank=True)
    
    # Pole pro předplatné
    subscription_type = models.CharField(max_length=20, choices=[
        ('free', 'Free Plan'),
        ('basic', 'Basic Plan'),
        ('pro', 'Pro Plan'),
        ('premium', 'Premium Plan')
    ], default='free')
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    virtual_try_ons_remaining = models.IntegerField(default=5)
    profile_images_remaining = models.IntegerField(default=3)
    try_on_results_remaining = models.IntegerField(default=7)

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
            'basic': (50, 5, 20),
            'pro': (100, 8, 40),
            'premium': (300, 20, 60)
        }
        self.virtual_try_ons_remaining, self.profile_images_remaining, self.try_on_results_remaining = limits.get(self.subscription_type, (5, 3, 7))

    def use_feature(self, feature_type):
        if not self.is_subscription_active and self.subscription_type != 'free':
            return False, "Your subscription is not active"

        if feature_type == 'virtual_try_on':
            if self.virtual_try_ons_remaining > 0:
                self.virtual_try_ons_remaining -= 1
                self.save(update_fields=['virtual_try_ons_remaining'])
                return True, "Virtual try-on used successfully"
            return False, "No virtual try-ons remaining"
        elif feature_type == 'profile_image':
            if self.profile_images_remaining > 0:
                self.profile_images_remaining -= 1
                self.save(update_fields=['profile_images_remaining'])
                return True, "Profile image slot used successfully"
            return False, "No profile image slots remaining"
        elif feature_type == 'try_on_result':
            if self.try_on_results_remaining > 0:
                self.try_on_results_remaining -= 1
                self.save(update_fields=['try_on_results_remaining'])
                return True, "Try-on result used successfully"
            return False, "No try-on results remaining"
        return False, "Invalid feature type"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_subscription_type = None
        if not is_new:
            old_user = CustomUser.objects.get(pk=self.pk)
            old_subscription_type = old_user.subscription_type

        super().save(*args, **kwargs)

        if is_new or (old_subscription_type and old_subscription_type != self.subscription_type):
            self.reset_monthly_limits()
            super().save(update_fields=['virtual_try_ons_remaining', 'profile_images_remaining', 'try_on_results_remaining'])

    def __str__(self):
        return self.username

class FavoriteItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.product.name}"