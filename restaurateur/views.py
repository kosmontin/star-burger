import requests
from geopy import distance
from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from star_burger import settings


from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    menu = list(RestaurantMenuItem.objects.filter(availability=True).values(
        'product_id', 'restaurant__name', 'restaurant__address'))

    orders = Order.objects.total_cost().exclude(
        status='Done').prefetch_related('client', 'items')
    for order in orders:
        valid_order_coordinates = fetch_coordinates(order.address)
        if order.status == 'New':
            available_rests = dict()
            for order_product in order.items.all():
                for menu_item in menu:
                    if order_product.product_id == menu_item['product_id']:
                        available_rests.setdefault(
                            menu_item['restaurant__name'],
                            [0, menu_item['restaurant__address']])
                        available_rests[menu_item['restaurant__name']][0] += 1

            restaurants_who_can_do = []
            if valid_order_coordinates:
                for rest, values in available_rests.items():
                    rest_coordinates = fetch_coordinates(values[1])
                    if values[0] == order.items.count():
                        restaurants_who_can_do.append({
                            'name': rest,
                            'distance': round(
                                distance.distance(
                                    rest_coordinates,
                                    valid_order_coordinates).km, 2)
                        })
                order.restaurants = sorted(restaurants_who_can_do,
                                           key=lambda restaurant: restaurant[
                                               'distance'])
            else:
                order.restaurants = None

    return render(request, template_name='order_items.html', context={
        'order_items': orders
    })


def fetch_coordinates(address=None, apikey=settings.YANDEX_GEO_APIKEY):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
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
