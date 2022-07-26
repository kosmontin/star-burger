# Generated by Django 3.2 on 2022-07-26 10:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geodata', '0001_initial'),
        ('foodcartapp', '0051_alter_restaurant_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='geodata.address', verbose_name='адрес'),
        ),
    ]