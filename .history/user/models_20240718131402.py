from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from shop.models import Product
from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import timedelta

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    shopping_region = models.CharField(max_length=100)
    profile_images = models.JSONField(default=list, blank=True)
    
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

    def update_subscription(self, new_type, duration=30):
        self.subscription_type = new_type
        self.subscription_start_date = timezone.now()
        self.subscription_end_date = self.subscription_start_date + timedelta(days=duration)
        self.reset_monthly_limits()
        super().save()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_subscription_type = None
        if not is_new:
            old_user = CustomUser.objects.get(pk=self.pk)
            old_subscription_type = old_user.subscription_type

        if is_new or (old_subscription_type and old_subscription_type != self.subscription_type):
            self.reset_monthly_limits()
            self.subscription_start_date = timezone.now()
            self.subscription_end_date = self.subscription_start_date + timedelta(days=30)
            super().save(update_fields=['virtual_try_ons_remaining', 'profile_images_remaining', 'try_on_results_remaining', 'subscription_start_date', 'subscription_end_date'])
        else:
            super().save(*args, **kwargs)

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

@receiver(pre_save, sender=CustomUser)
def update_subscription_on_change(sender, instance, **kwargs):
    if instance.pk:
        old_instance = CustomUser.objects.get(pk=instance.pk)
        if old_instance.subscription_type != instance.subscription_type:
            instance.update_subscription(instance.subscription_type)
