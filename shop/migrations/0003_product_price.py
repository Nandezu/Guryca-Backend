# Generated by Django 5.0.6 on 2024-06-26 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_product_colour'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='price',
            field=models.CharField(default='0', max_length=50),
        ),
    ]
