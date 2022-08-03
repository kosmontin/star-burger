from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum, F
from django.utils import timezone

import geodata.models


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.ForeignKey(
        geodata.models.Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='адрес',
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Client(models.Model):
    firstname = models.CharField(verbose_name='Имя', max_length=50)
    lastname = models.CharField(
        verbose_name='Фамилия', max_length=50, db_index=True)

    phonenumber = models.CharField(
        db_index=True, max_length=20, verbose_name='телефон для связи')

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class OrderQuerySet(models.QuerySet):
    def total_cost(self):
        return self.annotate(
            total_cost=Sum(F('items__quantity') * F('items__price')))


class Order(models.Model):
    ORDER_STATUS = [
        ('New', 'Необработанный'),
        ('Processing', 'Собирается'),
        ('Delivering', 'Доставляется'),
        ('Done', 'Завершенный')
    ]
    PAYMENT_METHOD = [
        ('undefined', 'Не определен'),
        ('cash', 'Наличные'),
        ('card', 'Карта')
    ]
    registered_at = models.DateTimeField(
        default=timezone.now, db_index=True, verbose_name='создан')
    called_at = models.DateTimeField(
        null=True, blank=True, verbose_name='подтвержден')
    delivered_at = models.DateTimeField(
        null=True, blank=True, verbose_name='доставлен')
    status = models.CharField(
        max_length=15, choices=ORDER_STATUS, db_index=True,
        default='New', verbose_name='статус заказа')
    payment_method = models.CharField(
        max_length=15, choices=PAYMENT_METHOD, db_index=True,
        default='undefined', verbose_name='способ оплаты')
    client = models.ForeignKey(
        Client, on_delete=models.SET_NULL, null=True,
        related_name='orders', verbose_name='клиент')
    address = models.ForeignKey(
        geodata.models.Address, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='адрес доставки заказа')
    comment = models.TextField(null=True, blank=True,
                               verbose_name='комментарий')
    which_restaurant_doing = models.ForeignKey(
        Restaurant, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='processed_orders',
        verbose_name='какой ресторан готовит заказ'
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ №{self.pk}'


class OrderPoint(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT,
        related_name='order_points', verbose_name='товар')
    price = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0), ],
        default=0, verbose_name='цена')
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        default=1, verbose_name='количество')
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items',
        verbose_name='номер заказа')

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f'Заказ №{self.order.pk}, {self.product.name}'
