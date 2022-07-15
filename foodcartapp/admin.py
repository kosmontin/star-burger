from django.contrib import admin
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from star_burger import settings
from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from .models import Client
from .models import Order
from .models import OrderPoint


class OrderInline(admin.StackedInline):
    model = Order
    extra = 0


class OrderPointInline(admin.StackedInline):
    model = OrderPoint
    extra = 0


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    inlines = [OrderInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fields = ('status', 'which_restaurant_doing', 'registered_at', 'called_at',
              'delivered_at', 'payment_method', 'client',
              'get_phonenumber', 'address', 'comment')
    radio_fields = {'status': admin.VERTICAL}
    readonly_fields = ['registered_at', 'client', 'get_phonenumber', 'address']
    inlines = [OrderPointInline]

    @admin.display(description='Номер телефона')
    def get_phonenumber(self, obj):
        return obj.client.phonenumber

    def response_post_save_change(self, request, obj):
        res = super().response_post_save_change(request, obj)
        if 'next' in request.GET and url_has_allowed_host_and_scheme(
                request.GET['next'], settings.ALLOWED_HOSTS):
            return HttpResponseRedirect(request.GET['next'])
        else:
            return res

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super(OrderAdmin, self).get_form(request, obj, **kwargs)
        qs = Restaurant.objects.filter(
            menu_items__product_id__in=obj.items.values('product')).annotate(
            rest_counter=Count('menu_items__restaurant_id')).filter(
            rest_counter__gte=obj.items.count())
        form.base_fields['which_restaurant_doing'].queryset = qs
        return form
