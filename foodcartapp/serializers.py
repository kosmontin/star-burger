import phonenumbers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from .models import Client, Order, OrderPoint


class ClientSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = ('firstname', 'lastname', 'phonenumber')

    def validate_phonenumber(self, value):
        phone = phonenumbers.parse(value, 'RU')
        if phonenumbers.is_valid_number(phone):
            return phonenumbers.format_number(
                phone, phonenumbers.PhoneNumberFormat.E164)
        else:
            raise ValidationError('Unsupported phonenumber format')

    def create(self, validated_data):
        client, _ = Client.objects.get_or_create(**validated_data)
        return client


class OrderPointSerializer(ModelSerializer):
    class Meta:
        model = OrderPoint
        fields = ('product', 'quantity', 'price')

    def create(self, validated_data):
        validated_data['price'] = validated_data['product'].price

        return OrderPoint.objects.create(**validated_data)


class OrderSerializer(ModelSerializer):
    items = OrderPointSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'address', 'client', 'items')
        depth = 1

    def create(self, validated_data):
        return Order.objects.create(**validated_data)
