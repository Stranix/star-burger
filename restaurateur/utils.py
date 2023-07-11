from geopy import distance

from foodcartapp.models import Restaurant

from geolocation.utils import distance_formatter
from geolocation.utils import get_or_create_locations


def get_orders_suitable_restaurants_with_locations(orders):
    order_addresses = [order.address for order in orders]
    restaurant_addresses = [
        restaurant.address for restaurant in Restaurant.objects.all()
    ]
    locations = get_or_create_locations(
        *order_addresses, *restaurant_addresses
    )
    for order in orders:
        order_location = locations.get(order.address, None)

        for restaurant in order.suitable_restaurants:
            restaurant_location = locations.get(restaurant.address, None)
            if not (order_location and restaurant_location):
                restaurant.distance = 0
                restaurant.readable_distance = 0
                continue
            restaurant.distance = distance.distance(
                order_location, restaurant_location
            ).km
            restaurant.readable_distance = distance_formatter(
                restaurant.distance
            )

        sorted_suitable_restaurants = sorted(
            order.suitable_restaurants,
            key=lambda restaurant: restaurant.distance
        )
        order.suitable_restaurants = sorted_suitable_restaurants

    return orders
