from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    store_link = models.URLField()
    image_url = models.URLField()
    sku = models.CharField(max_length=100)
    clothing_type = models.CharField(max_length=50, choices=[('top', 'Top'), ('bottom', 'Bottom'), ('full', 'Full')])
    clothing_category = models.CharField(max_length=50)
    manufacturer_name = models.CharField(max_length=255)
    country_of_origin = models.CharField(max_length=100)
    colour = models.CharField(max_length=100, default='unknown')
    price = models.CharField(max_length=50)  # Přidání pole pro cenu

    def __str__(self):
        return self.name