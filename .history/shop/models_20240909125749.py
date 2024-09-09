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

    name = models.CharField(max_length=21, default='Default Name')

    store_link = models.URLField(max_length=1000)
    image_url = models.URLField()
    sku = models.CharField(max_length=100)
    clothing_type = models.CharField(max_length=50, choices=CLOTHING_TYPE_CHOICES, default='upper_body')
    clothing_category = models.CharField(max_length=50, choices=CLOTHING_CATEGORY_CHOICES)
    manufacturer_name = models.CharField(max_length=17)
    country_of_origin = models.CharField(max_length=100, choices=COUNTRY_CHOICES, default='usa')  # Přidejte výchozí hodnotu
    colour = models.CharField(max_length=5, choices=COLOUR_CHOICES, default='light')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Použijte DecimalField pro cenu

    def __str__(self):
        return self.name
