# Generated by Django 3.2 on 2022-07-26 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_alter_order_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='address',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='адрес'),
        ),
    ]
