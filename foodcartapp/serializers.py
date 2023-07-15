from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField

from .models import Order
from .models import OrderElement
from .models import Product


class OrderElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderElement
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderElementSerializer(
        many=True,
        allow_empty=False,
        write_only=True
    )
    phonenumber = PhoneNumberField(region='RU')

    class Meta:
        model = Order
        fields = [
            'id',
            'firstname',
            'lastname',
            'address',
            'phonenumber',
            'products',
        ]

    def create(self, validated_data):
        order_products_validated_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        order_products = []
        for item_payload in order_products_validated_data:
            item_payload['order'] = order
            item_payload['price'] = Product.objects.get(
                name=item_payload['product']
            ).price
            order_products.append(OrderElement(**item_payload))
        OrderElement.objects.bulk_create(order_products)
        return order
