import requests
from django.db import models

from star_burger import settings


class Address(models.Model):
    address = models.CharField(
        max_length=100, verbose_name='адрес', unique=True)
    lon = models.FloatField(verbose_name='долгота', null=True, blank=True)
    lat = models.FloatField(verbose_name='широта', null=True, blank=True)
    updated_at = models.DateField('дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'

    def __str__(self):
        return self.address


def fetch_coordinates(address=None, apikey=settings.YANDEX_GEO_APIKEY):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection'][
        'featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lat, lon = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat
