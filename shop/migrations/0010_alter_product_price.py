# Generated by Django 5.0.6 on 2024-09-09 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_remove_product_country_of_origin_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.CharField(default='0 USD', max_length=15),
        ),
    ]