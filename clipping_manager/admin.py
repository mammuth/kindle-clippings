from django.contrib import admin

from clipping_manager.models import Clipping, Book, EmailDelivery


@admin.register(Clipping)
class ClippingAdmin(admin.ModelAdmin):
    pass


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(EmailDelivery)
class EmailDeliveryAdmin(admin.ModelAdmin):
    search_fields = ('user', )
    list_display = ('user', 'interval', 'last_delivery', )