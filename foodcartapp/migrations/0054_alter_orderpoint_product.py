# Generated by Django 3.2 on 2022-08-03 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0053_alter_orderpoint_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderpoint',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_points', to='foodcartapp.product', verbose_name='товар'),
        ),
    ]