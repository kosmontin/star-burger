# Generated by Django 3.2 on 2022-08-15 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0064_alter_order_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, verbose_name='описание'),
        ),
    ]