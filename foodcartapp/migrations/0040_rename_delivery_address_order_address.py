# Generated by Django 3.2 on 2022-06-22 08:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_rename_contact_phone_client_phonenumber'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='delivery_address',
            new_name='address',
        ),
    ]