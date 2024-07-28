from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from shop.models import Product  # Předpokládá se, že Product je v aplikaci 'shop'

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    shopping_region = models.CharField(max_length=100)
    profile_images = models.JSONField(default=list, blank=True)
    
    # Nová pole pro předplatné
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
        """
        Vrátí URL prvního profilového obrázku, pokud existuje.
        Jinak vrátí None.
        """
        return self.profile_images[0] if self.profile_images else None

    @property
    def is_subscription_active(self):
        if self.subscription_type == 'free':
            return True
        return self.subscription_end_date > timezone.now() if self.subscription_end_date else False

    def reset_monthly_limits(self):
        if self.subscription_type == 'free':
            self.virtual_try_ons_remaining = 5
            self.profile_images_remaining = 3
            self.try_on_results_remaining = 7
        elif self.subscription_type == 'basic':
            self.virtual_try_ons_remaining = 50
            self.profile_images_remaining = 5
            self.try_on_results_remaining = 20
        elif self.subscription_type == 'pro':
            self.virtual_try_ons_remaining = 100
            self.profile_images_remaining = 8
            self.try_on_results_remaining = 40
        elif self.subscription_type == 'premium':
            self.virtual_try_ons_remaining = 300
            self.profile_images_remaining = 20
            self.try_on_results_remaining = 60
        self.save()

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