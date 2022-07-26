# Generated by Django 3.2 on 2022-07-26 10:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geodata', '0001_initial'),
        ('foodcartapp', '0049_alter_order_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='geodata.address', verbose_name='адрес доставки заказа'),
        ),
    ]
