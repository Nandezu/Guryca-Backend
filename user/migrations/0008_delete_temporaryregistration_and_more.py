# Generated by Django 5.0.6 on 2024-08-09 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_temporaryregistration'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TemporaryRegistration',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='confirmation_code',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='confirmation_code_created_at',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='email_confirmed',
        ),
    ]
