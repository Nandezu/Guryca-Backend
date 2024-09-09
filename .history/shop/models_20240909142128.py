import random
import string
from django.db import models

class Product(models.Model):
    CLOTHING_TYPE_CHOICES = [
        ('upper_body', 'Upper Body'),
        ('lower_body', 'Lower Body'),
        ('dresses', 'Dresses'),
    ]

    CLOTHING_CATEGORY_CHOICES = [
        ('dress', 'Dress'),
        ('top', 'Top'),
        ('jeans', 'Jeans'),
        ('jumpsuit', 'Jumpsuit'),
        ('short', 'Short'),
        ('jacket', 'Jacket'),
        ('sweatpants', 'Sweatpants'),
        ('skirt', 'Skirt'),
        ('sweater', 'Sweater'),
        ('pants', 'Pants'),
        ('leggings', 'Leggings'),
        ('coat', 'Coat'),
    ]

    COLOUR_CHOICES = [
        ('light', 'Light'),
    ]

    name = models.CharField(max_length=21, default='Default Name')
    store_link = models.URLField(max_length=1000)
    image_url = models.URLField()
    sku = models.CharField(max_length=100, unique=True, blank=True)
    clothing_type = models.CharField(max_length=50, choices=CLOTHING_TYPE_CHOICES, default='upper_body')
    clothing_category = models.CharField(max_length=50, choices=CLOTHING_CATEGORY_CHOICES)
    manufacturer_name = models.CharField(max_length=17)
    colour = models.CharField(max_length=5, choices=COLOUR_CHOICES, default='light')
    price = models.DecimalField(max_digits=10,  default=0)

    def save(self, *args, **kwargs):
        if not self.sku:  # Pokud SKU není nastavené, generuj nové
            self.sku = self.generate_sku()
        super(Product, self).save(*args, **kwargs)

    def generate_sku(self):
        """Generuje náhodné SKU."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    def formatted_price(self):
        """Vrátí cenu formátovanou s USD."""
        return f"{self.price} USD"

    def __str__(self):
        return self.name