from django.db import models

class Product(models.Model):
    CLOTHING_TYPE_CHOICES = [
        ('upper_body', 'Upper Body'),
        ('lower_body', 'Lower Body'),
        ('dresses', 'Dresses'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    store_link = models.URLField()
    image_url = models.URLField()
    sku = models.CharField(max_length=100)
    clothing_type = models.CharField(max_length=50, choices=CLOTHING_TYPE_CHOICES, default='upper_body')
    clothing_category = models.CharField(max_length=50)
    manufacturer_name = models.CharField(max_length=255)
    country_of_origin = models.CharField(max_length=100)
    colour = models.CharField(max_length=100, default='unknown')
    price = models.CharField(max_length=50, default='0')

    def __str__(self):
        return self.name