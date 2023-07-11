from django.db import models


class Location(models.Model):
    address = models.CharField('адрес', max_length=100, unique=True)
    lat = models.FloatField('широта', null=True, blank=True)
    lon = models.FloatField('долгота', null=True, blank=True)
    updated_at = models.DateTimeField(
        'дата запроса к геокодеру',
        auto_now=True,
    )

    def __str__(self):
        return f'{self.address} ({self.lat}, {self.lon})'
