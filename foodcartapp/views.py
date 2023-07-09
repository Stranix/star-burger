import phonenumbers
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product
from .models import Order
from .models import OrderElement


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    serialized_order = request.data

    required_fields = ['products', 'firstname', 'lastname', 'phonenumber',
                       'address']
    for field in required_fields:
        if field not in serialized_order.keys():
            return Response(
                {'error': f'{field} - required field'},
                status.HTTP_406_NOT_ACCEPTABLE
            )

    order_products = serialized_order['products']
    first_name = serialized_order['firstname']
    last_name = serialized_order['lastname']
    address = serialized_order['address']
    phonenumber = serialized_order['phonenumber']

    if not isinstance(order_products, list):
        return Response(
            {'error': 'products - must be a list'},
            status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    if not order_products:
        return Response(
            {'error': 'products - non-empty field'},
            status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    if not all(list(map(lambda field: isinstance(field, str),
                        [first_name, last_name, address, phonenumber]))):
        return Response(
            {'error': 'fields firstname, lastname, address, '
                      'phonenumber must be strings'},
            status=status.HTTP_406_NOT_ACCEPTABLE
        )

    try:
        parsed_phonenumber = phonenumbers.parse(phonenumber, "RU")
    except phonenumbers.phonenumberutil.NumberParseException:
        return Response(
            {'error': 'The string supplied did not seem to be a phone number'},
            status=status.HTTP_406_NOT_ACCEPTABLE
        )

    if not phonenumbers.is_valid_number(parsed_phonenumber):
        return Response(
            {'error': 'invalid phone number'},
            status=status.HTTP_406_NOT_ACCEPTABLE
        )
    formatted_phonenumber = phonenumbers.format_number(
        parsed_phonenumber,
        phonenumbers.PhoneNumberFormat.E164
    )

    order = Order.objects.create(
        address=address,
        firstname=first_name,
        lastname=last_name,
        phonenumber=formatted_phonenumber,
    )

    for product in order_products:
        product_id = product['product']
        product_quantity = product['quantity']
        try:
            product_instance = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'invalid product id'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        OrderElement.objects.create(
            order=order,
            product=product_instance,
            quantity=product_quantity,
        )
    return Response(serialized_order, status.HTTP_201_CREATED)
