import json

import phonenumbers
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Client, Order, OrderPoint, Product


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
    deserialized_order = request.data

    phone = phonenumbers.parse(
        deserialized_order['phonenumber'], 'RU')
    if phonenumbers.is_valid_number(
        phone) and phonenumbers.is_possible_number(phone):
        normalized_phonenumber = phone
    else:
        normalized_phonenumber = ''

    client, _ = Client.objects.get_or_create(
        firstname=deserialized_order['firstname'],
        lastname=deserialized_order['lastname'],
        contact_phone=normalized_phonenumber
    )

    order = Order.objects.create(
        client=client,
        delivery_address=deserialized_order['address']
    )

    for product in deserialized_order['products']:
        OrderPoint.objects.create(
            product=Product.objects.get(pk=product['product']),
            quantity=product['quantity'],
            order=order
        )
    return Response({'order': deserialized_order})
