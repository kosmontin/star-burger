# Generated by Django 3.2 on 2022-07-05 06:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_alter_client_phonenumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderpoint',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='цена'),
        ),
    ]
