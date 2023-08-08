import requests

from django.conf import settings

from geolocation.models import Location


def fetch_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": settings.YANDEX_GEO_API_KEY,
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


def distance_formatter(distance):
    distance_with_units = f"{int(distance)} км"
    if distance < 10:
        distance_with_units = f"{distance:.2f} км"
    if distance < 1:
        distance_with_units = f"{int(distance * 1000)} м"
    return distance_with_units


def get_or_create_locations(*addresses):
    existed_locations = {
        location.address: (location.lat, location.lon)
        for location in Location.objects.filter(address__in=addresses)
    }

    for address in addresses:
        if address in existed_locations.keys():
            continue

        try:
            coordinates = fetch_coordinates(address)
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            KeyError,
        ):
            continue

        if not coordinates:
            continue

        lat, lon = coordinates
        location = Location.objects.create(address=address, lon=lon, lat=lat)
        existed_locations[location.address] = (location.lat, location.lon)

    return existed_locations
