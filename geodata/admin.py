from django.contrib import admin, messages

from .models import Address, fetch_coordinates


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('address', 'lon', 'lat', 'updated_at',)
    fields = ('address', 'lon', 'lat', 'updated_at',)
    readonly_fields = ('updated_at',)
    actions = ['update_geo']

    @admin.action(description='Обновить геоданные у выбранных адресов')
    def update_geo(self, request, queryset):
        for obj in queryset:
            try:
                lat, lon = fetch_coordinates(address=obj.address)
                obj.lat = lat
                obj.lon = lon
                obj.save()
            except:
                messages.add_message(
                    request, messages.ERROR, 'Ошибка обновления геоданных')

    def response_post_save_change(self, request, obj):
        res = super(AddressAdmin, self).response_post_save_change(request, obj)
        try:
            lat, lon = fetch_coordinates(address=obj.address)
            obj.lat = lat
            obj.lon = lon
            obj.save()
        except:
            messages.add_message(
                request, messages.ERROR, 'Ошибка обновления геоданных')
        return res

    def save_model(self, request, obj, form, change):
        try:
            lat, lon = fetch_coordinates(address=obj.address)
            obj.lat = lat
            obj.lon = lon
        except:
            messages.add_message(
                request, messages.ERROR, 'Ошибка обновления геоданных')
        finally:
            obj.save()
