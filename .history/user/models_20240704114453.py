from django.db import models
from django.contrib.auth.models import AbstractUser
from shop.models import Product  # Předpokládá se, že Product je v aplikaci 'shop'

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    shopping_region = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    profile_image_url = models.URLField(max_length=500, null=True, blank=True)

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