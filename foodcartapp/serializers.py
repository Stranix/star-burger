import phonenumbers
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Order
from .models import OrderElement


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

    def validate_phonenumber(self, value):
        if not phonenumbers.is_valid_number(phonenumbers.parse(value, 'RU')):
            raise ValidationError('Не верный номер телефона')
        return value
