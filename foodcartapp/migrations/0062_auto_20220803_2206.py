# Generated by Django 3.2 on 2022-08-03 19:06

from django.db import migrations
import phonenumbers


def normalize_phonenumbers(apps, schema_editor):
    Client = apps.get_model('foodcartapp', 'Client')
    for client in Client.objects.all():
        phone = phonenumbers.parse(client.phonenumber.raw_input, 'RU')
        if phonenumbers.is_valid_number(phone):
            client.phonenumber = phonenumbers.format_number(
                phone, phonenumbers.PhoneNumberFormat.E164)
            client.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0061_alter_client_phonenumber'),
    ]

    operations = [
        migrations.RunPython(normalize_phonenumbers)
    ]
