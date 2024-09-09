from django.db import models
import uuid

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
        ('short', 'short'),
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
        ('dark', 'Dark'),
    ]

    COUNTRY_CHOICES = [
        ('usa', 'USA'),
        ('united_kingdom', 'United Kingdom'),
        ('germany', 'Germany'),
        ('brazil', 'Brazil'),
        ('italy', 'Italy'),
        ('france', 'France'),
        ('spain', 'Spain'),
        ('poland', 'Poland'),
        ('czech_republic', 'Czech Republic'),
        ('slovakia', 'Slovakia'),
    ]

    store_link = models.URLField(max_length=1000)
    image_url = models.URLField()
    clothing_type = models.CharField(max_length=50, choices=CLOTHING_TYPE_CHOICES, default='upper_body')
    clothing_category = models.CharField(max_length=50, choices=CLOTHING_CATEGORY_CHOICES)
    manufacturer_name = models.CharField(max_length=17)
    colour = models.CharField(max_length=5, choices=COLOUR_CHOICES, default='light')
    price = models.CharField(max_length=50, default='0')
    sku = models.CharField(max_length=100, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = str(uuid.uuid4())  # Generuje náhodný UUID
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name