import phonenumbers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from .models import Client, Order, OrderItem


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


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('product', 'quantity', 'price')

    def create(self, validated_data):
        validated_data['price'] = validated_data['product'].price

        return OrderItem.objects.create(**validated_data)


class OrderSerializer(ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'registered_at', 'called_at', 'delivered_at',
                  'status', 'payment_method', 'address', 'comment',
                  'which_restaurant_doing', 'client', 'items')
        depth = 1

    def create(self, validated_data):
        return Order.objects.create(**validated_data)
