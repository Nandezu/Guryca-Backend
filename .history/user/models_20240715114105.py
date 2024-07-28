from django.db import models
from django.contrib.auth.models import AbstractUser
from shop.models import Product  # Předpokládá se, že Product je v aplikaci 'shop'

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    shopping_region = models.CharField(max_length=100)
    profile_images = models.JSONField(default=list, blank=True)
    
    @property
    def active_profile_image(self):
        """
        Vrátí URL prvního profilového obrázku, pokud existuje.
        Jinak vrátí None.
        """
        return self.profile_images[0]['url'] if self.profile_images else None

    def add_profile_image(self, image_url, is_from_image_detail=False):
        """
        Přidá nový profilový obrázek.
        """
        self.profile_images.append({
            'url': image_url,
            'is_from_image_detail': is_from_image_detail
        })
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