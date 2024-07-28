from django.db import models
from user.models import CustomUser
from shop.models import Product

class TryOnResult(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    result_image = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Try-on result for {self.user.username} and {self.product.name}"