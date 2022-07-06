from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, Product
from .serializers import ClientSerializer, OrderSerializer, \
    OrderPointSerializer


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


class RegisterOrderAPIView(APIView):
    def get(self, request):
        orders = Order.objects.all()
        orders_serializer = OrderSerializer(orders, many=True)
        return Response({'orders': orders_serializer.data})

    def post(self, request):
        client_serializer = ClientSerializer(data=request.data)
        client_serializer.is_valid(raise_exception=True)

        order_serializer = OrderSerializer(data=request.data)
        order_serializer.is_valid(raise_exception=True)

        products = request.data.get('products', [])
        if isinstance(products, str):
            raise ValidationError(
                'products: expected list field with values, got str.')
        elif not products:
            raise ValidationError(
                'products: field required and must be not empty.')

        order_points = OrderPointSerializer(data=products, many=True)
        order_points.is_valid(raise_exception=True)

        with transaction.atomic():
            client = client_serializer.save()
            order = order_serializer.save(client=client)
            order_points.save(order=order)

        return Response({'order': order_serializer.data})
