# Generated by Django 5.0.6 on 2024-09-09 10:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_remove_product_country_of_origin_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='sku',
        ),
    ]