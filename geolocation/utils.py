import requests

from django.conf import settings
from django.utils import timezone
from geopy import distance

from .models import Location


def fetch_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": settings.YANDEX_API_KEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection'][
        'featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_distance(address_from, address_to):
    coords_from = fetch_coordinates(address_from)
    coords_to = fetch_coordinates(address_to)
    return distance.distance(coords_from, coords_to).km


def distance_formatter(distance):
    distance_with_units = f"{int(distance)} км"
    if distance < 10:
        distance_with_units = f"{distance:.2f} км"
    if distance < 1:
        distance_with_units = f"{int(distance * 1000)} м"
    return distance_with_units


def get_or_create_locations(*addresses):
    print(addresses)
    locations = []
    existed_locations = {
        location.address: (location.lat, location.lon)
        for location in Location.objects.filter(address__in=addresses)
    }
    print(existed_locations)
    for address in addresses:
        if address in existed_locations.keys():
            locations.append(existed_locations[address])
        else:
            coordinates = fetch_coordinates(address)
            if not coordinates:
                locations.append(None)
                continue
            lat, lon = coordinates
            Location.objects.create(address=address, lon=lon, lat=lat, updated_at=timezone.now())
            locations.append(coordinates)
    print(locations)
    return locations
